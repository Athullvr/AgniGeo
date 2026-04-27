
# 🔥 AgniGeo

**Physics-Informed Deep Learning for India-wide Urban Thermal Comfort Prediction**

> Predicting human-perceived heat stress (UTCI) at street level across Indian cities
> using multimodal satellite data, urban morphology, and physics-informed neural networks.

---

## 🎯 What AgniGeo Does

Standard satellite data gives you **Land Surface Temperature (LST)** — what the ground feels like.
AgniGeo predicts **UTCI (Universal Thermal Climate Index)** — what a *human body* actually experiences
on the street, accounting for radiation, wind, humidity, and urban geometry.

**Output:** 1m–30m resolution UTCI maps for any Indian city, generated in minutes instead of hours.

---

## 🏗️ Architecture

```
Inputs                    Model                     Output
──────                    ─────                     ──────
nDSM (building heights) ─┐
Land cover / NDVI        ├─► U-Net Encoder
Sky View Factor          │       │
LST (Sentinel/Landsat)  ─┘       │ FiLM fusion ◄── Met variables
                                  │             (Ta, RH, wind, radiation)
                                  ▼
                           GNN (urban graph)
                                  │
                           PINN loss (physics)
                                  │
                                  ▼
                           UTCI map (1–30m)
```

**Teacher model:** SOLWEIG (via UMEP) — generates ground-truth labels
**Student model:** AgniGeo — 1000× faster inference

---

## 📁 Project Structure

```
agnigeo/
├── configs/
│   └── config.yaml           # All city bboxes, model params, paths
├── data/
│   ├── raw/
│   │   ├── osm/              # Building footprints, roads, landuse
│   │   ├── era5/             # Meteorological reanalysis
│   │   ├── dem/              # Cartosat/SRTM elevation
│   │   └── sentinel/         # Satellite imagery
│   └── processed/
│       ├── ndsm/             # Normalized Digital Surface Models
│       ├── landcover/        # Classified land cover rasters
│       └── utci_labels/      # SOLWEIG-generated UTCI training labels
├── src/
│   ├── data/
│   │   ├── download.py       # OSM + ERA5 downloader
│   │   ├── preprocess.py     # Raster alignment, nDSM generation
│   │   └── dataset.py        # PyTorch Dataset class
│   ├── models/
│   │   ├── unet.py           # U-Net backbone
│   │   ├── film.py           # FiLM conditioning module
│   │   ├── gnn.py            # Graph Neural Network (Phase 3)
│   │   └── agnigeo.py        # Full unified model
│   ├── physics/
│   │   ├── utci.py           # UTCI calculation utilities
│   │   ├── radiation.py      # Stefan-Boltzmann, Tmrt equations
│   │   └── pinn_loss.py      # Physics-Informed loss terms
│   └── utils/
│       ├── config.py         # Config loader
│       └── metrics.py        # MAE, RMSE, R² for UTCI
├── notebooks/
│   ├── 01_verify_environment.ipynb
│   ├── 02_explore_kochi_osm.ipynb    # (Phase 2)
│   └── 03_first_utci_prediction.ipynb # (Phase 2)
├── scripts/
│   └── setup_env.sh          # One-shot environment installer
├── outputs/
│   └── maps/                 # Generated UTCI maps
└── requirements.txt
```

---

## 🗺️ Roadmap

| Phase | Months | Goal |
|-------|--------|------|
| 1 | 1–3 | Environment + SOLWEIG running on Thrissur |
| 2 | 3–6 | First DL model — UTCI for Kochi (10m res) |
| 3 | 6–9 | PINN + GNN unified model, paper draft |
| 4 | 9–12 | 5 Indian climate zones, transfer learning |
| 5 | 12–14 | India-wide 30m inference system |
| 6 | 14–15 | Prototype deployed, journal paper submitted |

---

## 📚 Key References

- GSM-UTCI (UPenn, 2025): https://arxiv.org/abs/2507.23000
- PINN for MRT (2025): https://arxiv.org/abs/2503.08482
- UHTC-NN 1m resolution: https://www.sciencedirect.com/science/article/pii/S2212095525002809
- Urban canyon UTCI factors (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC12179017/

---

## 📍 Pilot City

**Kochi + Thrissur, Kerala, India**
Climate zone: Aw (Tropical savanna)
Target seasons: Pre-monsoon (March–May) + Post-monsoon (October–November)

Kerala's high humidity and monsoon seasonality makes AgniGeo's PINN physics terms
more challenging — and more globally distinctive — than existing European/US work.

---

*AgniGeo — Agni (fire/heat) + Geo (spatial). Built for the cities that need it most.*
