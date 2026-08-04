import pytest
from src.physics.utci import calculate_utci
pytest.importorskip("pythermalcomfort")

@pytest.mark.parametrize(("ta","tr","wind","rh","expected"), [(25.,25.,1.,50.,24.6), (40.,25.,1.,50.,40.6)])
def test_utci_documented_reference_examples(ta, tr, wind, rh, expected):
    """Examples from pythermalcomfort's Bröde et al. UTCI implementation."""
    assert calculate_utci(ta, tr, wind, rh) == pytest.approx(expected, abs=.2)

def test_utci_vectorized_inputs():
    assert calculate_utci([25.,30.], [25.,30.], [1.,1.], [50.,50.]).shape == (2,)
