# AgniGeo

Physics-informed urban thermal-comfort research for India. AgniGeo predicts street-level UTCI (Universal Thermal Climate Index), rather than land-surface temperature, using urban geometry, weather and satellite/geospatial inputs.

## Current status

**Phase 1 is complete and empirically verified.** The project generated two real SOLWEIG UTCI rasters for the Thrissur, Kerala pilot area from SRTM terrain, 3,563 OpenStreetMap building footprints, and ERA5 meteorology. No synthetic UTCI labels were used.

| Scenario | UTC timestamp | UTCI range | SOLWEIG runtime |
| --- | --- | --- | --- |
| Pre-monsoon | 2024-04-15 12:00 | 33.16–34.14 °C | 0.596 s |
| Post-monsoon | 2024-11-15 12:00 | 32.53–33.23 °C | 0.359 s |

The 30 m pilot DSM has no missing cells. Full reproducibility evidence is in [outputs/phase1_validation.json](outputs/phase1_validation.json). Raw and intermediate geospatial files remain untracked.

## What Phase 1 includes

- Scriptable standalone SOLWEIG teacher integration.
- ERA5 GRIB parsing for temperature, dew point, 10 m wind and solar radiation.
- OSM building-height rasterisation, with a documented 9 m fallback when OSM has no height tags.
- SRTM DEM reprojection, aligned DSM construction and sky-view-factor QA proxy.
- Real pre- and post-monsoon UTCI label generation for Thrissur.
- UTCI and preprocessing tests (`6 passed`).

Run the validated pipeline with:

```powershell
.\.tools\python313\python.exe -c "import sys,runpy; sys.path.insert(0,'.'); runpy.run_path('scripts/run_phase1_thrissur.py', run_name='__main__')"
```

## Roadmap

| Phase | Status | Goal |
| --- | --- | --- |
| 1 | Complete | Thrissur inputs, real SOLWEIG labels, validation |
| 2 | Not started | Kochi SOLWEIG label set and U-Net + FiLM baseline |
| 3 | Not started | Physics-informed loss and urban graph model |
| 4–6 | Not started | Multi-city transfer, India-wide inference, prototype viewer |

Phase 2 must use real Kochi SOLWEIG labels and is intentionally not started by this repository update.

## References

- [GSM-UTCI](https://arxiv.org/abs/2507.23000)
- [PINN for MRT](https://arxiv.org/abs/2503.08482)
- [UHTC-NN](https://www.sciencedirect.com/science/article/pii/S2212095525002809)
- [Urban canyon UTCI factors](https://pmc.ncbi.nlm.nih.gov/articles/PMC12179017/)
- Lindberg et al. (2008), SOLWEIG 1.0, doi:10.1007/s00484-008-0162-7
