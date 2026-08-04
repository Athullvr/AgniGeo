"""Explicit, credential-free OSM and ERA5 acquisition."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
from src.utils.config import load_config

def download_osm(city: str, bbox: list[float], output_root: str | Path = "data/raw/osm") -> dict[str, Path]:
    """Fetch buildings, land use and drivable roads only when explicitly invoked."""
    try: import osmnx as ox
    except ImportError as exc: raise RuntimeError("Install osmnx before downloading OSM data.") from exc
    west, south, east, north = bbox; root = Path(output_root) / city; root.mkdir(parents=True, exist_ok=True)
    def features(tags):
        # OSMnx 1.x used four bounds; 2.x uses one bbox tuple.
        try: return ox.features_from_bbox((north, south, east, west), tags=tags)
        except TypeError: return ox.features_from_bbox(north, south, east, west, tags=tags)
    def graph():
        try: return ox.graph_from_bbox((north, south, east, west), network_type="drive", simplify=True)
        except TypeError: return ox.graph_from_bbox(north, south, east, west, network_type="drive", simplify=True)
    result = {}
    for name, tags in {"buildings":{"building":True}, "landuse":{"landuse":True,"natural":True,"leisure":True}}.items():
        gdf = features(tags)
        path = root / f"{name}.geojson"; gdf.to_file(path, driver="GeoJSON"); result[name] = path
    roads = ox.graph_to_gdfs(graph(), nodes=False, edges=True); path = root / "roads.geojson"; roads.to_file(path, driver="GeoJSON"); result["roads"] = path
    return result

def download_era5(city: str, bbox: list[float], timestamp: str, output_root: str | Path = "data/raw/era5") -> Path:
    """Request one ERA5 hour using a user-provided CDS API configuration."""
    if not (os.getenv("CDSAPI_URL") and os.getenv("CDSAPI_KEY")):
        raise RuntimeError("Set CDSAPI_URL and CDSAPI_KEY; credentials are never stored in this project.")
    try:
        import cdsapi; import pandas as pd
    except ImportError as exc: raise RuntimeError("Install cdsapi and pandas first.") from exc
    west, south, east, north = bbox; moment = pd.Timestamp(timestamp)
    target = Path(output_root) / city / f"era5_{moment:%Y%m%dT%H%MZ}.nc"; target.parent.mkdir(parents=True, exist_ok=True)
    cdsapi.Client().retrieve("reanalysis-era5-single-levels", {"product_type":"reanalysis", "variable":["2m_temperature","2m_dewpoint_temperature","10m_u_component_of_wind","10m_v_component_of_wind","surface_solar_radiation_downwards"], "year":f"{moment:%Y}", "month":f"{moment:%m}", "day":f"{moment:%d}", "time":f"{moment:%H}:00", "area":[north,west,south,east], "format":"netcdf"}, str(target))
    return target

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--city", default="thrissur"); p.add_argument("--scenario", default="thrissur_pre_monsoon"); p.add_argument("--osm-only", action="store_true"); a = p.parse_args()
    cfg = load_config(); bbox = cfg["cities"][a.city]["bbox"]; print(download_osm(a.city, bbox))
    if not a.osm_only: print(download_era5(a.city, bbox, cfg["scenarios"][a.scenario]["timestamp_utc"]))
if __name__ == "__main__": main()
