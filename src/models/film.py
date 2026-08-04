"""Feature-wise Linear Modulation for scalar meteorological conditioning."""
from __future__ import annotations

import torch
from torch import nn


class FiLM(nn.Module):
    def __init__(self, condition_features: int, channels: int) -> None:
        super().__init__()
        self.affine = nn.Sequential(nn.Linear(condition_features, channels * 2), nn.SiLU(), nn.Linear(channels * 2, channels * 2))
        self.channels = channels

    def forward(self, features: torch.Tensor, condition: torch.Tensor) -> torch.Tensor:
        gamma, beta = self.affine(condition).chunk(2, dim=1)
        return features * (1 + gamma[:, :, None, None]) + beta[:, :, None, None]
