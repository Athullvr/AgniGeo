# Manual data required for scientific validation

The software can be built without these files, but no phase below is scientifically complete until its listed data and measurements exist. Raw data remains gitignored.

| Phase | Required manual data | Validation evidence |
| --- | --- | --- |
| 2 | Kochi 10 m DEM/DSM; OSM buildings; at least 7, ideally 12, ERA5 scenarios; Kochi LST and NDVI | Real SOLWEIG UTCI labels; spatial held-out MAE/RMSE/R²; same-area runtime comparison |
| 3 | The Phase 2 label set plus inputs needed to compute absorbed radiation/Tmrt; urban graph geometry | Three real ablations: U-Net+FiLM, +PINN, +GNN |
| 4 | Real SOLWEIG labels and equivalent raster inputs for climate-distinct cities (minimum one each from BSh, Cwa, BWh, Cfa) | Fine-tuning metrics at 100%, 50%, and 10% labels for every target city |
| 5 | A validated Phase 3 checkpoint; inputs for each requested city (DEM/DSM, OSM, LST, NDVI, scenario weather) | Resumable tiled output checked against the model’s reference inference |
| 6 | Validated Phase 5 output GeoTIFFs and their scenario metadata | Visual inspection that displayed georeferencing, colour scale, timestamp, and units match the source raster |

## Current Phase 2 files to add

- `data/raw/dem/kochi_dem.tif` — genuine 10 m DEM/DSM.
- `data/raw/era5/era5_kochi_*.grib` — seven or more correctly named/validated scenarios.
- `data/raw/sentinel/kochi_lst.tif` and `data/raw/sentinel/kochi_ndvi.tif` — real satellite-derived model channels.

Do not replace any item above with synthetic labels, interpolated “truth”, or upsampled 30 m elevation when evaluating a 10 m claim.
