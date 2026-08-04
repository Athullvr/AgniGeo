import pytest
from src.utils.metrics import speedup, utci_metrics


def test_metrics_perfect_prediction():
    result = utci_metrics([30, 31, 32], [30, 31, 32])
    assert result["mae_c"] == 0 and result["rmse_c"] == 0 and result["r2"] == 1


def test_speedup_requires_positive_model_time():
    with pytest.raises(ValueError): speedup(1, 0)
