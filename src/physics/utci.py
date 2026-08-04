"""UTCI via the vetted pythermalcomfort package; never hand-roll the polynomial."""
from __future__ import annotations
import numpy as np

def calculate_utci(air_temperature_c, mean_radiant_temperature_c, wind_speed_m_s, relative_humidity_percent):
    """Return UTCI °C. Source: Bröde et al. 2012, doi:10.1007/s00484-011-0454-1."""
    try: from pythermalcomfort.models import utci
    except ImportError as exc: raise RuntimeError("Install pythermalcomfort to calculate UTCI.") from exc
    value = np.asarray(utci(tdb=air_temperature_c, tr=mean_radiant_temperature_c, v=wind_speed_m_s, rh=relative_humidity_percent, limit_inputs=False).utci, dtype=float)
    return float(value) if value.ndim == 0 else value
