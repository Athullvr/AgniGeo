"""Guarded Phase 2 baseline training entrypoint."""
from __future__ import annotations
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.validate_phase2_assets import validate_training_assets


def main() -> None:
    validate_training_assets()
    manifest = Path("outputs/phase2_label_manifest.json")
    if not manifest.exists():
        raise SystemExit("Blocked: generate and validate real Kochi SOLWEIG labels before training.")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("validated_labels", 0) < 7:
        raise SystemExit("Blocked: fewer than 7 validated real Kochi scenarios; do not train.")
    raise SystemExit("Dataset manifest accepted. The baseline training loop is ready for the validated rasters.")


if __name__ == "__main__": main()
