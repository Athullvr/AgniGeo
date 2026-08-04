"""Raster preparation utilities used before real SOLWEIG runs."""
from __future__ import annotations
from pathlib import Path
import numpy as np

def building_height_from_tags(tags: dict, default_height_m: float = 9.0, story_height_m: float = 3.0) -> float:
    raw = tags.get("height")
    if raw is not None:
        try:
            height = float(str(raw).lower().replace("m", "").strip())
            if np.isfinite(height):
                return height
        except ValueError: pass
    try:
        levels = float(tags["building:levels"])
        if np.isfinite(levels):
            return levels * story_height_m
    except (KeyError, TypeError, ValueError): return default_height_m  # Missing tags assume a 3-storey, 9m building.
    return default_height_m  # GeoPandas represents absent OSM fields as NaN.

def generate_ndsm(dem: np.ndarray, building_height_m: np.ndarray, building_mask: np.ndarray | None = None) -> np.ndarray:
    dem, heights = np.asarray(dem, dtype=np.float32), np.asarray(building_height_m, dtype=np.float32)
    if dem.shape != heights.shape: raise ValueError("DEM and building-height grids must be aligned.")
    if building_mask is not None: heights = np.where(np.asarray(building_mask, dtype=bool), heights, 0)
    return dem + np.maximum(heights, 0)

def sky_view_factor_from_height(height_above_ground_m: np.ndarray, resolution_m: float, search_radius_m: float = 50.) -> np.ndarray:
    """Local-horizon SVF proxy for QA; use UMEP's rigorous calculation in SOLWEIG."""
    h = np.asarray(height_above_ground_m, dtype=np.float32)
    if h.ndim != 2 or resolution_m <= 0: raise ValueError("height must be 2D and resolution positive.")
    radius = max(1, round(search_radius_m / resolution_m)); padded = np.pad(h, radius, mode="edge"); horizon = np.zeros_like(h)
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            distance = np.hypot(dx, dy)
            if not distance or distance > radius: continue
            n = padded[radius+dy:radius+dy+h.shape[0], radius+dx:radius+dx+h.shape[1]]
            horizon = np.maximum(horizon, np.maximum(n-h, 0) / (distance*resolution_m))
    return np.clip(1 - np.arctan(horizon)/(np.pi/2), 0, 1).astype(np.float32)

def align_raster(source_path: str | Path, reference_path: str | Path, output_path: str | Path) -> Path:
    import rasterio
    from rasterio.warp import Resampling, reproject
    with rasterio.open(reference_path) as ref, rasterio.open(source_path) as src:
        profile = ref.profile.copy(); profile.update(dtype="float32", count=1, nodata=np.nan)
        dst = np.full((ref.height, ref.width), np.nan, dtype=np.float32)
        reproject(rasterio.band(src,1), dst, src_transform=src.transform, src_crs=src.crs, dst_transform=ref.transform, dst_crs=ref.crs, resampling=Resampling.bilinear)
        output = Path(output_path); output.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(output, "w", **profile) as f: f.write(dst, 1)
    return output
