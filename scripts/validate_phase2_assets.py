"""Validate real-data prerequisites for Phase 2.

Teacher-label production and student-model training use different inputs.  Keeping
their gates separate means a valid SOLWEIG run is never delayed by an optional
student channel, while training can still never silently proceed without one.
"""
from __future__ import annotations
from pathlib import Path
import yaml


ROOT = Path(__file__).parents[1]


def _missing_paths(paths: list[Path]) -> list[str]:
    return [str(path.relative_to(ROOT)) for path in paths if not path.exists()]


def teacher_assets() -> tuple[list[str], int]:
    manifest = yaml.safe_load((ROOT / "configs/phase2_kochi_scenarios.yaml").read_text(encoding="utf-8"))
    required = [ROOT / "data/raw/dem/kochi_dem.tif", ROOT / "data/raw/osm/kochi/buildings.geojson"]
    missing = _missing_paths(required)
    era5 = list((ROOT / "data/raw/era5").glob("era5_kochi_*.grib"))
    if len(era5) < 7:
        missing.append("at least 7 correctly named, valid Kochi ERA5 GRIB files")
    return missing, len(era5)


def validate_teacher_assets() -> None:
    missing, era5_count = teacher_assets()
    if missing:
        print("Blocked: these real assets are required for SOLWEIG teacher labels:")
        print("\n".join(f"- {item}" for item in missing))
        raise SystemExit(1)
    print(f"Teacher-label gate passed with {era5_count} ERA5 files.")


def validate_training_assets() -> None:
    validate_teacher_assets()
    missing = _missing_paths([
        ROOT / "data/raw/sentinel/kochi_lst.tif",
        ROOT / "data/raw/sentinel/kochi_ndvi.tif",
    ])
    if missing:
        print("Blocked: these additional assets are required for student-model training:")
        print("\n".join(f"- {item}" for item in missing))
        raise SystemExit(1)
    print("Training-input gate passed.")


def main() -> None:
    validate_training_assets()


if __name__ == "__main__": main()
