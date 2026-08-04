"""Patch dataset for real SOLWEIG-labelled raster scenarios only."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import numpy as np


@dataclass(frozen=True)
class ScenarioRaster:
    inputs: tuple[Path, ...]
    label: Path
    meteorology: tuple[float, float, float, float]  # Ta, RH, wind, global radiation
    scenario_id: str


class UTCIPatchDataset:
    """Tile aligned input/teacher rasters; split by tile positions, never pixels."""
    def __init__(self, scenarios: Sequence[ScenarioRaster], patch_size: int = 64, tile_indices: Sequence[tuple[int, int, int]] | None = None) -> None:
        try:
            import rasterio
            import torch
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Install rasterio and torch before creating the dataset.") from exc
        self.rasterio, self.torch, self.scenarios, self.patch_size = rasterio, torch, list(scenarios), patch_size
        if not self.scenarios:
            raise ValueError("At least one real SOLWEIG scenario is required.")
        with rasterio.open(self.scenarios[0].label) as label:
            height, width = label.height, label.width
        indices = [(scenario, row, col) for scenario in range(len(self.scenarios)) for row in range(0, height - patch_size + 1, patch_size) for col in range(0, width - patch_size + 1, patch_size)]
        self.indices = indices if tile_indices is None else list(tile_indices)

    def __len__(self) -> int: return len(self.indices)

    def __getitem__(self, index: int):
        scenario_index, row, col = self.indices[index]
        scenario = self.scenarios[scenario_index]
        window = self.rasterio.windows.Window(col, row, self.patch_size, self.patch_size)
        def read(path: Path) -> np.ndarray:
            with self.rasterio.open(path) as dataset:
                return dataset.read(1, window=window, masked=True).filled(np.nan).astype(np.float32)
        features, target = np.stack([read(path) for path in scenario.inputs]), read(scenario.label)
        if not np.isfinite(features).all() or not np.isfinite(target).all():
            raise ValueError(f"NoData inside patch for scenario {scenario.scenario_id} at ({row}, {col}).")
        return self.torch.from_numpy(features), self.torch.tensor(scenario.meteorology), self.torch.from_numpy(target[None, ...])


def geographic_split(dataset: UTCIPatchDataset, validation_fraction: float = 0.2) -> tuple[list[int], list[int]]:
    """Hold out the eastern geographic tile strip, avoiding random-pixel leakage."""
    cutoff = np.quantile([col for _, _, col in dataset.indices], 1 - validation_fraction)
    train = [index for index, (_, _, col) in enumerate(dataset.indices) if col < cutoff]
    validation = [index for index, (_, _, col) in enumerate(dataset.indices) if col >= cutoff]
    return train, validation
