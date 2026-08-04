"""Create a small tracked manifest only after real Kochi SOLWEIG rasters exist."""
from __future__ import annotations
import json
from pathlib import Path
import rasterio
import numpy as np


ROOT = Path(__file__).parents[1]


def main() -> None:
    labels = sorted((ROOT / "data/processed/utci_labels/kochi").glob("*_utci.tif"))
    if len(labels) < 7:
        raise SystemExit("Blocked: at least 7 real Kochi SOLWEIG UTCI rasters are required.")
    entries = []
    for label in labels:
        with rasterio.open(label) as dataset:
            values = dataset.read(1, masked=True).compressed()
            if not values.size or not np.isfinite(values).all():
                raise ValueError(f"Invalid teacher raster: {label}")
            entries.append({"path": str(label.relative_to(ROOT)), "shape": [dataset.height, dataset.width], "utci_min_c": float(values.min()), "utci_max_c": float(values.max())})
    output = ROOT / "outputs/phase2_label_manifest.json"
    output.write_text(json.dumps({"validated_labels": len(entries), "labels": entries}, indent=2), encoding="utf-8")
    print(f"Wrote {output} with {len(entries)} validated real labels.")


if __name__ == "__main__": main()
