import pytest
pytest.importorskip("torch")
from src.data.dataset import ScenarioRaster, UTCIPatchDataset


def test_dataset_requires_real_scenarios():
    with pytest.raises(ValueError): UTCIPatchDataset([])
