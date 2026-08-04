"""Phase 4 guardrail: transfer experiments cannot run without validated Phase 3."""
from __future__ import annotations
from pathlib import Path


def main() -> None:
    evidence = Path("outputs/phase3_ablation_metrics.json")
    if not evidence.exists():
        raise SystemExit("Blocked: create real Phase 2 labels and validated Phase 3 ablations before transfer learning.")
    targets = sorted(Path("outputs/transfer_manifests").glob("*.json"))
    if not targets:
        raise SystemExit("Blocked: add real target-city SOLWEIG label manifests under outputs/transfer_manifests/.")
    print(f"Ready for real transfer experiments across {len(targets)} target-city manifests at label fractions 100%, 50%, 10%.")


if __name__ == "__main__": main()
