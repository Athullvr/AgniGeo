"""Non-GUI adapter for the official standalone SOLWEIG Python package."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from pathlib import Path
import shutil
import time

import numpy as np


class SolweigUnavailableError(RuntimeError):
    """Raised when the real teacher is unavailable; labels are never fabricated."""


@dataclass(frozen=True)
class SolweigRun:
    scenario: str
    output_path: Path
    elapsed_seconds: float


def run_solweig(scenario: str, input_rasters: dict[str, str | Path], meteorology: dict[str, float | str], output_path: str | Path) -> SolweigRun:
    """Create one real SOLWEIG UTCI raster from a projected DSM and observations.

    Required ``input_rasters`` entry: ``dsm``. Optional entries are ``dem`` and
    ``cdsm``. Required meteorology: ISO-8601 ``datetime``, ``ta`` (deg C), ``rh``
    (%), ``global_rad`` (W/m2), and ``ws`` (m/s). Location defaults to Thrissur
    unless ``latitude``, ``longitude``, and ``utc_offset`` are supplied.
    """
    try:
        import solweig
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SolweigUnavailableError("Install the official `solweig` package before creating labels.") from exc
    if "dsm" not in input_rasters:
        raise ValueError("SOLWEIG requires a projected DSM raster under input_rasters['dsm'].")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    timestamp = str(meteorology["datetime"]).replace("Z", "+00:00")
    utc_offset = float(meteorology.get("utc_offset", 5.5))
    # SOLWEIG's Weather datetime is a local, naive civil time; preserve sun angle.
    local_time = datetime.fromisoformat(timestamp).astimezone(timezone(timedelta(hours=utc_offset))).replace(tzinfo=None)
    weather = solweig.Weather(
        datetime=local_time, ta=float(meteorology["ta"]),
        rh=float(meteorology["rh"]), global_rad=float(meteorology["global_rad"]), ws=float(meteorology["ws"]),
    )
    location = solweig.Location(
        latitude=float(meteorology.get("latitude", 10.5276)), longitude=float(meteorology.get("longitude", 76.2144)),
        utc_offset=utc_offset,
    )
    # Per-scenario cache avoids Windows memmap locks between consecutive runs.
    surface_args = {"dsm": str(input_rasters["dsm"]), "working_dir": str(output.parent / f".{output.stem}_solweig_cache")}
    for key in ("dem", "cdsm"):
        if key in input_rasters:
            surface_args[key] = str(input_rasters[key])
    surface = solweig.SurfaceData.prepare(**surface_args)
    run_dir = output.parent / f".{output.stem}_solweig"
    started = time.perf_counter()
    solweig.calculate(surface=surface, weather=[weather], location=location, output_dir=str(run_dir), outputs=["utci"])
    elapsed = time.perf_counter() - started
    generated = run_dir / "summary" / "utci_mean.tif"
    if not generated.exists():
        raise RuntimeError("SOLWEIG completed without writing its UTCI summary GeoTIFF.")
    shutil.copyfile(generated, output)
    validate_utci_raster(output)
    return SolweigRun(scenario, output, elapsed)


def validate_utci_raster(path: str | Path, expected_range: tuple[float, float] = (20.0, 50.0)) -> None:
    """Reject empty or wildly implausible teacher outputs before they become labels."""
    import rasterio
    with rasterio.open(path) as dataset:
        values = dataset.read(1, masked=True).compressed()
    if not values.size:
        raise ValueError("SOLWEIG output has no valid pixels.")
    low, high = np.nanpercentile(values, [1, 99])
    if low < expected_range[0] - 10 or high > expected_range[1] + 10:
        raise ValueError(f"Suspicious UTCI ({low:.1f}-{high:.1f} C): check units and inputs before using labels.")
