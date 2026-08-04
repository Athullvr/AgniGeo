"""Phase 6 prototype viewer for validated UTCI GeoTIFF outputs."""
from pathlib import Path

import numpy as np


def main() -> None:
    import streamlit as st
    import rasterio
    import matplotlib.pyplot as plt
    st.set_page_config(page_title="AgniGeo UTCI viewer", layout="wide")
    st.title("AgniGeo — UTCI map viewer")
    maps = sorted(Path("outputs/maps").glob("*.tif"))
    if not maps:
        st.info("No validated UTCI GeoTIFFs in outputs/maps yet.")
        return
    selected = st.selectbox("Validated UTCI raster", maps, format_func=lambda item: item.name)
    with rasterio.open(selected) as dataset: values, bounds, crs = dataset.read(1, masked=True), dataset.bounds, dataset.crs
    fig, axis = plt.subplots(figsize=(10, 7)); image = axis.imshow(values, cmap="inferno", vmin=20, vmax=50); fig.colorbar(image, ax=axis, label="UTCI (°C)"); axis.set_title(selected.name); axis.set_axis_off()
    st.pyplot(fig); st.caption(f"CRS: {crs} | Bounds: {tuple(round(x, 5) for x in bounds)} | Range: {float(values.min()):.1f}–{float(values.max()):.1f} °C")


if __name__ == "__main__": main()
