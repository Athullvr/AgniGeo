"""Build real Thrissur SOLWEIG inputs and generate the two Phase 1 UTCI labels."""
from __future__ import annotations

import json
from math import ceil, floor, hypot
from pathlib import Path

import cfgrib
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds, reproject, Resampling

from src.data.preprocess import building_height_from_tags, generate_ndsm, sky_view_factor_from_height
from src.teacher.solweig_runner import run_solweig
from src.utils.config import load_config


ROOT = Path(__file__).parents[1]


def prepare_rasters(config: dict, city_name: str = "thrissur") -> dict[str, Path]:
    """Project DEM and real OSM footprints together on one native-resolution grid."""
    city = config["cities"][city_name]
    west, south, east, north = city["bbox"]
    crs, resolution = city["crs"], city["resolution_m"]
    minx, miny, maxx, maxy = transform_bounds("EPSG:4326", crs, west, south, east, north, densify_pts=21)
    minx, miny = floor(minx / resolution) * resolution, floor(miny / resolution) * resolution
    maxx, maxy = ceil(maxx / resolution) * resolution, ceil(maxy / resolution) * resolution
    width, height = int(round((maxx - minx) / resolution)), int(round((maxy - miny) / resolution))
    transform = from_origin(minx, maxy, resolution, resolution)
    profile = {"driver": "GTiff", "height": height, "width": width, "count": 1, "dtype": "float32", "crs": crs, "transform": transform, "nodata": -9999.0, "compress": "lzw"}
    out = ROOT / "data/processed/ndsm" / city_name; out.mkdir(parents=True, exist_ok=True)

    dem = np.full((height, width), -9999.0, dtype=np.float32)
    with rasterio.open(ROOT / "data/raw/dem" / f"{city_name}_dem.tif") as source:
        reproject(rasterio.band(source, 1), dem, src_transform=source.transform, src_crs=source.crs, src_nodata=source.nodata, dst_transform=transform, dst_crs=crs, dst_nodata=-9999.0, resampling=Resampling.bilinear)
    if np.any(dem == -9999.0):
        raise ValueError("DEM does not cover the complete configured Thrissur bbox.")

    buildings = gpd.read_file(ROOT / "data/raw/osm" / city_name / "buildings.geojson").to_crs(crs)
    default_height = config["preprocess"]["default_building_height_m"]
    story_height = config["preprocess"]["story_height_m"]
    shapes = [(geometry, building_height_from_tags(properties, default_height, story_height)) for geometry, properties in zip(buildings.geometry, buildings.drop(columns="geometry").to_dict("records")) if geometry is not None and not geometry.is_empty]
    building_height = rasterize(shapes, out_shape=dem.shape, transform=transform, fill=0, dtype="float32", all_touched=True)
    dsm = generate_ndsm(dem, building_height)
    svf = sky_view_factor_from_height(building_height, resolution, config["preprocess"]["svf_search_radius_m"])
    outputs = {"dem": out / "dem_30m.tif", "building_height": out / "building_height_30m.tif", "dsm": out / "dsm_30m.tif", "svf": out / "svf_proxy_30m.tif"}
    for name, values in {"dem": dem, "building_height": building_height, "dsm": dsm, "svf": svf}.items():
        with rasterio.open(outputs[name], "w", **profile) as dataset:
            dataset.write(values.astype(np.float32), 1)
    return outputs


def meteorology_from_grib(path: Path, latitude: float | None = None, longitude: float | None = None) -> dict[str, float | str]:
    """Extract one ERA5 point; SSRD accumulated energy is converted to mean W/m²."""
    datasets = cfgrib.open_datasets(str(path))
    weather = next(dataset for dataset in datasets if "t2m" in dataset.data_vars)
    radiation = next(dataset for dataset in datasets if "ssrd" in dataset.data_vars)
    if latitude is not None and longitude is not None:
        weather, radiation = weather.sel(latitude=latitude, longitude=longitude, method="nearest"), radiation.sel(latitude=latitude, longitude=longitude, method="nearest")
    values = {name: float(dataset[name].values) for dataset in (weather, radiation) for name in dataset.data_vars}
    duration_s = max(float(radiation.step.values / np.timedelta64(1, "s")), 3600.0)
    ta, dew = values["t2m"] - 273.15, values["d2m"] - 273.15
    # Magnus saturation-vapour-pressure relation (Alduchov & Eskridge, 1996) for RH.
    rh = 100 * np.exp((17.625 * dew) / (243.04 + dew) - (17.625 * ta) / (243.04 + ta))
    valid = str(weather.valid_time.values).replace(".000000000", "") + "Z"
    return {"datetime": valid, "ta": ta, "rh": float(np.clip(rh, 0, 100)), "ws": hypot(values["u10"], values["v10"]), "global_rad": values["ssrd"] / duration_s, "latitude": float(weather.latitude.values), "longitude": float(weather.longitude.values), "utc_offset": 5.5}


def main() -> None:
    config = load_config(ROOT / "configs/config.yaml")
    rasters = prepare_rasters(config)
    sources = {"thrissur_pre_monsoon": ROOT / "data/raw/era5/era5_thrissur_20240415T1200Z.grib", "thrissur_post_monsoon": ROOT / "data/raw/era5/era5_thrissur_20241115T1200Z.grib"}
    output_dir = ROOT / "data/processed/utci_labels/thrissur"; output_dir.mkdir(parents=True, exist_ok=True)
    report = {"rasters": {key: str(value.relative_to(ROOT)) for key, value in rasters.items()}, "runs": {}}
    for scenario, source in sources.items():
        meteorology = meteorology_from_grib(source)
        result = run_solweig(scenario, {"dsm": rasters["dsm"], "dem": rasters["dem"]}, meteorology, output_dir / f"{scenario}_utci.tif")
        report["runs"][scenario] = {"meteorology": meteorology, "utci_raster": str(result.output_path.relative_to(ROOT)), "solweig_wall_seconds": result.elapsed_seconds}
    (output_dir / "phase1_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
