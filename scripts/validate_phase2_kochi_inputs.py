"""Preflight check: refuse Phase 2 label generation until every real input exists."""
from __future__ import annotations

from pathlib import Path
import yaml


ROOT = Path(__file__).parents[1]


def main() -> None:
    manifest = yaml.safe_load((ROOT / "configs/phase2_kochi_scenarios.yaml").read_text(encoding="utf-8"))
    missing = []
    for path in (ROOT / "data/raw/dem/kochi_dem.tif", ROOT / "data/raw/osm/kochi/buildings.geojson"):
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
    for scenario in manifest["scenarios"]:
        stamp = scenario["timestamp_utc"].replace("-", "").replace(":", "").replace("Z", "Z")
        expected = ROOT / "data/raw/era5" / f"era5_kochi_{stamp}.grib"
        if not expected.exists():
            missing.append(str(expected.relative_to(ROOT)))
    if missing:
        print("Phase 2 is intentionally blocked: missing real teacher inputs:")
        print("\n".join(f"- {path}" for path in missing))
        raise SystemExit(1)
    print("All Kochi Phase 2 inputs are present. Real SOLWEIG label generation may start.")


if __name__ == "__main__":
    main()
