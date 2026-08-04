import pytest
torch = pytest.importorskip("torch")
from src.models.agnigeo import AgniGeo


def test_agnigeo_preserves_spatial_shape():
    model = AgniGeo(spatial_channels=4, meteorology_features=4, base_channels=8)
    output = model(torch.randn(2, 4, 32, 32), torch.randn(2, 4))
    assert output.shape == (2, 1, 32, 32)
