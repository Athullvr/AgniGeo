"""Benchmark gate; cannot claim speedup until real model inference is available."""
from __future__ import annotations
import json
from pathlib import Path
from src.utils.metrics import speedup


def main() -> None:
    teacher = Path("outputs/phase2_teacher_runtime.json")
    model = Path("outputs/phase2_model_runtime.json")
    if not teacher.exists() or not model.exists():
        raise SystemExit("Blocked: record real SOLWEIG and model wall-clock times for the same Kochi area.")
    teacher_seconds = json.loads(teacher.read_text())["seconds"]
    model_seconds = json.loads(model.read_text())["seconds"]
    print(json.dumps({"solweig_seconds": teacher_seconds, "model_seconds": model_seconds, "measured_speedup": speedup(teacher_seconds, model_seconds)}, indent=2))


if __name__ == "__main__": main()
