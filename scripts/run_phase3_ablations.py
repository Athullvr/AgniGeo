"""Guarded Phase 3 ablation orchestrator; does not fabricate experiment metrics."""
from __future__ import annotations
import json
from pathlib import Path
import yaml


def main() -> None:
    labels = Path("outputs/phase2_label_manifest.json")
    if not labels.exists() or json.loads(labels.read_text()).get("validated_labels", 0) < 7:
        raise SystemExit("Blocked: Phase 3 needs at least 7 validated real Phase 2 SOLWEIG labels.")
    plan = yaml.safe_load(Path("configs/phase3_phase4_plan.yaml").read_text())
    print("Ready to run real ablations:", ", ".join(plan["phase3"]["ablations"]))
    print("Provide radiation/Tmrt targets and a geographic urban graph before running this command.")


if __name__ == "__main__": main()
