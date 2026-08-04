"""Unified student model. GNN remains opt-in until Phase 3 ablation data exists."""
from __future__ import annotations

import torch
from torch import nn
from src.models.film import FiLM
from src.models.unet import UNet


class AgniGeo(nn.Module):
    def __init__(self, spatial_channels: int, meteorology_features: int = 4, base_channels: int = 32) -> None:
        super().__init__()
        self.unet = UNet(spatial_channels, base_channels)
        self.film = FiLM(meteorology_features, self.unet.bottleneck_channels)
    def forward(self, spatial: torch.Tensor, meteorology: torch.Tensor) -> torch.Tensor:
        skip, bottleneck = self.unet.forward_features(spatial)
        return self.unet.decode(skip, self.film(bottleneck, meteorology))
