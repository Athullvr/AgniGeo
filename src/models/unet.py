"""Compact U-Net backbone used by the Phase 2/3 student model."""
from __future__ import annotations

import torch
from torch import nn


class ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(nn.Conv2d(in_channels, out_channels, 3, padding=1), nn.GroupNorm(1, out_channels), nn.SiLU(), nn.Conv2d(out_channels, out_channels, 3, padding=1), nn.GroupNorm(1, out_channels), nn.SiLU())
    def forward(self, x: torch.Tensor) -> torch.Tensor: return self.layers(x)


class UNet(nn.Module):
    def __init__(self, in_channels: int, base_channels: int = 32) -> None:
        super().__init__()
        self.enc1, self.enc2 = ConvBlock(in_channels, base_channels), ConvBlock(base_channels, base_channels * 2)
        self.pool, self.up = nn.MaxPool2d(2), nn.ConvTranspose2d(base_channels * 2, base_channels, 2, stride=2)
        self.dec, self.out = ConvBlock(base_channels * 2, base_channels), nn.Conv2d(base_channels, 1, 1)
        self.bottleneck_channels = base_channels * 2
    def forward_features(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        skip = self.enc1(x); return skip, self.enc2(self.pool(skip))
    def decode(self, skip: torch.Tensor, bottleneck: torch.Tensor) -> torch.Tensor:
        return self.out(self.dec(torch.cat((self.up(bottleneck), skip), dim=1)))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        skip, bottleneck = self.forward_features(x); return self.decode(skip, bottleneck)
