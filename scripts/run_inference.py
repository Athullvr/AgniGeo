"""Phase 5 tiled, resumable inference for a validated TorchScript checkpoint."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def tile_windows(height: int, width: int, tile_size: int, overlap: int):
    step = tile_size - overlap
    if step <= 0: raise ValueError("overlap must be smaller than tile_size")
    for row in range(0, height, step):
        for col in range(0, width, step):
            yield row, col, min(tile_size, height - row), min(tile_size, width - col)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run tiled AgniGeo UTCI inference.")
    parser.add_argument("--model", required=True, help="Validated exported TorchScript (.ts) checkpoint")
    parser.add_argument("--inputs", required=True, help="Directory containing ndsm.tif, svf.tif, lst.tif, ndvi.tif")
    parser.add_argument("--output", required=True)
    parser.add_argument("--meteorology", required=True, help="JSON object: Ta, RH, wind, radiation")
    parser.add_argument("--tile-size", type=int, default=256); parser.add_argument("--overlap", type=int, default=32)
    args = parser.parse_args()
    try:
        import rasterio, torch
    except ImportError as exc: raise SystemExit("Install rasterio and torch for inference.") from exc
    model_path, input_dir, output = Path(args.model), Path(args.inputs), Path(args.output)
    channels = [input_dir / f"{name}.tif" for name in ("ndsm", "svf", "lst", "ndvi")]
    if not model_path.exists() or any(not path.exists() for path in channels): raise SystemExit("Missing validated model or required input raster channels.")
    weather = json.loads(args.meteorology)
    required = ("Ta", "RH", "wind", "radiation")
    if any(key not in weather for key in required): raise SystemExit(f"Meteorology must contain {required}.")
    output.parent.mkdir(parents=True, exist_ok=True); state = output.with_suffix(".progress.json")
    with rasterio.open(channels[0]) as ref:
        profile = ref.profile.copy(); profile.update(count=1, dtype="float32", nodata=np.nan, compress="lzw")
        height, width = ref.height, ref.width
    done = set(json.loads(state.read_text()).get("done", [])) if state.exists() else set()
    model = torch.jit.load(str(model_path), map_location="cpu").eval()
    prediction = np.full((height, width), np.nan, dtype=np.float32)
    if output.exists():
        with rasterio.open(output) as dataset: prediction = dataset.read(1)
    for row, col, rows, cols in tile_windows(height, width, args.tile_size, args.overlap):
        key = f"{row}:{col}"
        if key in done: continue
        with rasterio.open(channels[0]) as first:
            arrays = [first.read(1, window=rasterio.windows.Window(col, row, cols, rows))]
        for channel in channels[1:]:
            with rasterio.open(channel) as dataset: arrays.append(dataset.read(1, window=rasterio.windows.Window(col, row, cols, rows)))
        x = torch.from_numpy(np.stack(arrays)[None].astype(np.float32)); m = torch.tensor([[weather[k] for k in required]], dtype=torch.float32)
        with torch.no_grad(): prediction[row:row+rows, col:col+cols] = model(x, m).squeeze().numpy()[:rows, :cols]
        with rasterio.open(output, "w", **profile) as dataset: dataset.write(prediction, 1)
        done.add(key); state.write_text(json.dumps({"done": sorted(done)}), encoding="utf-8")
    state.unlink(missing_ok=True); print(f"Wrote {output}")


if __name__ == "__main__": main()
