# Manual next steps: Phase 2 to project completion

Raw data is intentionally not pushed to GitHub. Keep it in `data/raw/`; scripts validate it before running.

## Phase 2: Kochi labels and baseline

1. Add a genuine native **10 m Kochi DEM/DSM** as `data/raw/dem/kochi_dem.tif`. Do not upsample the existing 30 m SRTM data.
2. Obtain the Kochi OSM building footprints at `data/raw/osm/kochi/buildings.geojson`. The repository can attempt this with `python scripts/fetch_osm_buildings.py --city kochi`; save the file manually if public Overpass is unavailable.
3. Download the five remaining corrected ERA5 scenarios: 2024-04-15 03:00 and 11:00 UTC; 2024-05-15 03:00 and 11:00 UTC; and 2024-10-15 11:00 UTC. The seven verified files are already staged locally, but all 12 give a stronger dataset. Use the Kochi request box in `configs/config.yaml` and include 2 m temperature/dew point, 10 m wind components, and surface solar radiation.
4. Add aligned Kochi satellite rasters: `data/raw/sentinel/kochi_lst.tif` and `data/raw/sentinel/kochi_ndvi.tif`. These are required for model training, not for SOLWEIG teacher-label generation.
5. Run the Phase 2 validator and teacher-label script. Inspect every output UTCI GeoTIFF, then build the label manifest. Do not train or report accuracy until the labels are real and validated.

## Phase 3: physics and graph ablations

1. Produce real radiation/mean-radiant-temperature inputs from the validated scenarios.
2. Build urban graph geometry from buildings and streets for each Kochi sample.
3. Run and report the three ablations on the same spatial hold-out: U-Net + FiLM; plus physics loss; plus graph module. Record MAE, RMSE, R² and runtime.

## Phase 4: transfer across cities

1. Choose target cities spanning the planned climate groups.
2. For each city, repeat the Phase 2 acquisition: native DEM/DSM, OSM buildings, ERA5 scenarios, LST, NDVI and real SOLWEIG labels.
3. Evaluate fine-tuning with 100%, 50% and 10% of each target-city label set. Never use synthetic labels as ground truth.

## Phase 5: deployment-scale inference

1. Select only areas with all validated input channels and a validated Phase 3/4 checkpoint.
2. Run tiled, resumable inference and compare tiles with reference inference before publishing maps.

## Phase 6: viewer and final validation

1. Inspect each GeoTIFF's location, CRS, timestamp, units and UTCI colour range in the viewer.
2. Create a reproducibility record: input-source/version, scenario weather, checkpoint hash, evaluation split, metrics and hardware/runtime.
3. Report limitations clearly: DEM resolution, missing building heights, ERA5 spatial resolution, satellite acquisition time, and the number of independent city/scenario labels.

## Current status

- Seven verified Kochi ERA5 files are present locally and excluded from Git by design.
- The immediate blockers for teacher labels are the 10 m Kochi DEM/DSM and Kochi buildings GeoJSON.
- LST and NDVI are the next blockers after labels, before learned-model training.
