import pytest
torch = pytest.importorskip("torch")

from src.models.gnn import UrbanGraphLayer
from src.physics.radiation import blackbody_exitance, tmrt_from_absorbed_flux


def test_radiation_inverse_is_consistent():
    temperature = torch.tensor([20.0, 35.0])
    recovered = tmrt_from_absorbed_flux(blackbody_exitance(temperature, emissivity=0.95), emissivity=0.95)
    assert torch.allclose(recovered, temperature, atol=1e-4)


def test_urban_graph_layer_preserves_node_feature_shape():
    layer = UrbanGraphLayer(4)
    output = layer(torch.randn(3, 4), torch.eye(3))
    assert output.shape == (3, 4)
