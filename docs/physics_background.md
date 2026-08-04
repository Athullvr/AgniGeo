# Physics background

UTCI estimates perceived heat stress from air temperature, humidity, wind and mean radiant temperature (Tmrt). It differs from land-surface temperature because it represents thermal load on a person. SOLWEIG is AgniGeo's teacher because it models shading and radiation from terrain/building geometry; its real output, never a substitute, is the source of training labels.

Tmrt combines short- and long-wave radiation from the sky, ground and buildings. Thus building height and sky-view factor matter in street canyons. Phase 1 intentionally stops at preparing and validating the teacher pipeline.

References: [GSM-UTCI](https://arxiv.org/abs/2507.23000), [PINN for MRT](https://arxiv.org/abs/2503.08482), [UHTC-NN](https://www.sciencedirect.com/science/article/pii/S2212095525002809), [urban canyon UTCI factors](https://pmc.ncbi.nlm.nih.gov/articles/PMC12179017/), and Bröde et al. (2012), doi:10.1007/s00484-011-0454-1.
