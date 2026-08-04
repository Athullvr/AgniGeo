# Raw data staging

This entire directory is ignored by git. Run `python -m src.data.download --city thrissur --scenario thrissur_pre_monsoon` after configuring `CDSAPI_URL` and `CDSAPI_KEY`; it writes OSM GeoJSON and ERA5 NetCDF below `osm/thrissur/` and `era5/thrissur/`.

Manually acquire a DEM (Cartosat/SRTM) as `dem/thrissur_dem.tif`, plus cloud-masked imagery as `sentinel/thrissur_lst.tif` and (if available) `sentinel/thrissur_ndvi.tif`. These inputs must have valid CRS metadata and are aligned to `configs/config.yaml` during preprocessing.

Install UMEP in QGIS or a supported standalone SOLWEIG program and expose a non-GUI wrapper in `AGNIGEO_SOLWEIG_COMMAND`. It receives `--request request.json` with paths and weather values and must write the requested GeoTIFF. AgniGeo will not generate labels until this real teacher is configured.
