import numpy as np
import pytest
from src.data.preprocess import generate_ndsm, sky_view_factor_from_height

def test_ndsm_adds_only_masked_buildings():
    result = generate_ndsm(np.array([[10,10],[11,11]]), np.array([[9,0],[12,6]]), np.array([[True,False],[True,False]]))
    np.testing.assert_allclose(result, [[19,10],[23,11]])
def test_ndsm_rejects_misaligned_grids():
    with pytest.raises(ValueError): generate_ndsm(np.ones((2,2)), np.ones((3,3)))
def test_svf_is_bounded_and_reduced_by_neighbor():
    flat = sky_view_factor_from_height(np.zeros((5,5)), 10)
    blocked = sky_view_factor_from_height(np.pad(np.array([[30.]],dtype=np.float32), 2), 10)
    assert np.all((flat >= 0) & (flat <= 1)) and blocked[2,1] < flat[2,1]
