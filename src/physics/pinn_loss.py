"""Phase 3 physics loss; unavailable for training until Phase 2 baseline validation."""
from __future__ import annotations

import torch
from torch.nn import functional as F
from src.physics.radiation import tmrt_from_absorbed_flux


def radiation_consistency_loss(predicted_tmrt_c: torch.Tensor, absorbed_flux_w_m2: torch.Tensor) -> torch.Tensor:
    """Penalize Tmrt inconsistent with the supplied absorbed radiative flux."""
    return F.smooth_l1_loss(predicted_tmrt_c, tmrt_from_absorbed_flux(absorbed_flux_w_m2))


def total_loss(data_loss: torch.Tensor, physics_loss: torch.Tensor, physics_weight: float) -> torch.Tensor:
    return data_loss + physics_weight * physics_loss
