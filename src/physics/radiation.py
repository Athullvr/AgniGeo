"""Differentiable radiative operations for the later PINN auxiliary loss."""
from __future__ import annotations

import torch

STEFAN_BOLTZMANN = 5.670374419e-8


def blackbody_exitance(temperature_c: torch.Tensor, emissivity: float = 1.0) -> torch.Tensor:
    """Return emitted long-wave flux (W/m²): εσT⁴.

    Source equation: ISO 7726 / Stefan-Boltzmann law. Inputs are converted to K.
    """
    return emissivity * STEFAN_BOLTZMANN * (temperature_c + 273.15).clamp_min(1.0).pow(4)


def tmrt_from_absorbed_flux(absorbed_flux_w_m2: torch.Tensor, emissivity: float = 0.95) -> torch.Tensor:
    """Invert εσT⁴ to derive mean radiant temperature in °C.

    This is a simplified radiative-equilibrium relation, not a replacement for
    SOLWEIG's directional radiation balance; use only as an auxiliary constraint.
    """
    return (absorbed_flux_w_m2.clamp_min(0) / (emissivity * STEFAN_BOLTZMANN)).pow(0.25) - 273.15
