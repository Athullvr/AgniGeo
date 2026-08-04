"""Optional Phase 3 graph layer for urban adjacency; no torch-geometric dependency."""
from __future__ import annotations

import torch
from torch import nn


class UrbanGraphLayer(nn.Module):
    def __init__(self, channels: int) -> None:
        super().__init__()
        self.self_projection, self.neighbour_projection = nn.Linear(channels, channels), nn.Linear(channels, channels)
    def forward(self, node_features: torch.Tensor, adjacency: torch.Tensor) -> torch.Tensor:
        """Apply a normalized message pass; adjacency shape is [nodes, nodes]."""
        weights = adjacency / adjacency.sum(dim=-1, keepdim=True).clamp_min(1)
        return torch.relu(self.self_projection(node_features) + self.neighbour_projection(weights @ node_features))
