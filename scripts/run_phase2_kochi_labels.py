"""Generate Kochi SOLWEIG labels from staged, real assets only."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import yaml

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.run_phase1_thrissur import ROOT, meteorology_from_grib, prepare_rasters
from src.teacher.solweig_runner import run_solweig
from scripts.validate_phase2_assets import validate_teacher_assets


def main() -> None:
    validate_teacher_assets()
    config = yaml.safe_load((ROOT / "configs/config.yaml").read_text(encoding="utf-8"))
    scenario_config = yaml.safe_load((ROOT / "configs/phase2_kochi_scenarios.yaml").read_text(encoding="utf-8"))
    rasters = prepare_rasters(config, "kochi")
    west, south, east, north = config["cities"]["kochi"]["bbox"]
    latitude, longitude = (south + north) / 2, (west + east) / 2
    output_dir = ROOT / "data/processed/utci_labels/kochi"; output_dir.mkdir(parents=True, exist_ok=True)
    report = {"city": "kochi", "rasters": {key: str(value.relative_to(ROOT)) for key, value in rasters.items()}, "runs": {}}
    for scenario in scenario_config["scenarios"]:
        stamp = scenario["timestamp_utc"].replace("-", "").replace(":", "")
        source = ROOT / "data/raw/era5" / f"era5_kochi_{stamp}.grib"
        if not source.exists():
            continue  # Seven validated scenarios are sufficient for a preliminary label set.
        meteorology = meteorology_from_grib(source, latitude, longitude)
        result = run_solweig(scenario["id"], {"dsm": rasters["dsm"], "dem": rasters["dem"]}, meteorology, output_dir / f"{scenario['id']}_utci.tif")
        report["runs"][scenario["id"]] = {"meteorology": meteorology, "utci_raster": str(result.output_path.relative_to(ROOT)), "solweig_wall_seconds": result.elapsed_seconds}
    if len(report["runs"]) < 7:
        raise RuntimeError("Fewer than 7 real Kochi labels were generated; do not train.")
    (output_dir / "phase2_teacher_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__": main()
