"""Evaluation and benchmark reporting utilities."""
from __future__ import annotations
import numpy as np


def utci_metrics(prediction, target) -> dict[str, float]:
    prediction, target = np.asarray(prediction, dtype=float).ravel(), np.asarray(target, dtype=float).ravel()
    valid = np.isfinite(prediction) & np.isfinite(target)
    if not valid.any(): raise ValueError("No finite prediction/target pairs.")
    prediction, target = prediction[valid], target[valid]
    error = prediction - target
    denominator = np.sum((target - target.mean()) ** 2)
    return {"mae_c": float(np.mean(np.abs(error))), "rmse_c": float(np.sqrt(np.mean(error ** 2))), "r2": float(1 - np.sum(error ** 2) / denominator) if denominator else float("nan")}


def speedup(solweig_seconds: float, model_seconds: float) -> float:
    if model_seconds <= 0: raise ValueError("Model runtime must be positive.")
    return solweig_seconds / model_seconds
