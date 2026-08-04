"""Inspect downloaded ERA5 GRIB files and safely stage valid Kochi scenarios.

Run without ``--copy`` first.  It never alters source downloads and only copies a
file after its valid time and nearest grid point match a configured scenario.
"""
from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path

import xarray as xr
import yaml


ROOT = Path(__file__).parents[1]
logging.getLogger("cfgrib.dataset").setLevel(logging.CRITICAL)


def grib_signature(path: Path) -> tuple[str, float, float]:
    """Return valid time and the first grid coordinate in a single-time GRIB."""
    dataset = xr.open_dataset(path, engine="cfgrib", backend_kwargs={"indexpath": ""})
    try:
        valid_time = str(dataset.valid_time.values.flat[0]).replace(" ", "T")[:19] + "Z"
        latitude = float(dataset.latitude.values.flat[0])
        longitude = float(dataset.longitude.values.flat[0])
        return valid_time, latitude, longitude
    finally:
        dataset.close()


def expected_scenarios() -> dict[str, str]:
    data = yaml.safe_load((ROOT / "configs/phase2_kochi_scenarios.yaml").read_text(encoding="utf-8"))
    return {item["timestamp_utc"]: item["id"] for item in data["scenarios"]}


def destination_name(timestamp_utc: str) -> str:
    return f"era5_kochi_{timestamp_utc.replace('-', '').replace(':', '')}.grib"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT, help="Folder containing downloaded .grib files")
    parser.add_argument("--copy", action="store_true", help="Copy verified files into data/raw/era5; default is dry-run")
    args = parser.parse_args()
    scenarios = expected_scenarios()
    staged = ROOT / "data/raw/era5"
    selected: dict[str, Path] = {}

    for path in sorted(args.source.glob("*.grib")):
        if path.parent == staged:
            continue
        try:
            timestamp, latitude, longitude = grib_signature(path)
        except Exception as exc:  # A corrupt/multi-message download is reported, never copied.
            print(f"REJECT {path.name}: cannot read a single ERA5 GRIB ({exc})")
            continue
        if timestamp not in scenarios:
            print(f"REJECT {path.name}: {timestamp} is not one of the 12 configured scenarios")
            continue
        if abs(latitude - 10.0) > 0.13 or abs(longitude - 76.25) > 0.13:
            print(f"REJECT {path.name}: grid point {latitude:.2f}, {longitude:.2f} is outside Kochi ERA5 coverage")
            continue
        if timestamp in selected:
            print(f"REJECT {path.name}: duplicate of {selected[timestamp].name} for {timestamp}")
            continue
        selected[timestamp] = path
        print(f"ACCEPT {path.name}: {scenarios[timestamp]} ({timestamp}, {latitude:.2f}, {longitude:.2f})")

    print(f"\nVerified {len(selected)} of {len(scenarios)} configured scenarios.")
    if args.copy:
        staged.mkdir(parents=True, exist_ok=True)
        for timestamp, source in selected.items():
            target = staged / destination_name(timestamp)
            shutil.copy2(source, target)
            print(f"COPIED {source.name} -> {target.relative_to(ROOT)}")
    elif selected:
        print("Dry run only. Re-run with --copy to stage the verified files.")


if __name__ == "__main__":
    main()
