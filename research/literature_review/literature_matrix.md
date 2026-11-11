# Literature Matrix: Pavement Distress & Road Damage Detection

This matrix benchmarks key peer-reviewed works that form the empirical baseline for RoadGuard.

| # | Reference | Dataset Used | Primary Architecture | Core Innovation | mAP / F1-Score | Inference Speed | Primary Limitation |
|---|---|---|---|---|---|---|---|
| **1** | **Maeda et al. (2018)**<br>*CACAIE* | RDD2018 (9k images, Japan) | SSD (MobileNet / Inception) | First crowdsourced smartphone dataset & mobile SSD benchmark | F1: 75.9% | 1.5 FPS (smartphone)<br>22.5 FPS (GPU) | Heavy miss rate on thin transverse cracks; vulnerable to road shadows. |
| **2** | **Arya et al. (2021)**<br>*Autom. Constr.* | GRDDC2020 (26k images, JP, IN, CZ) | Faster R-CNN, YOLOv4, SSD | Multi-country domain generalization analysis | F1: 67.3% (India), 77.8% (Japan) | 12 - 35 FPS | Cross-country domain shift reduced accuracy by up to 40% when unadapted. |
| **3** | **Arya et al. (2022)**<br>*IEEE BigData* | RDD2022 (47k images, 6 countries) | Ensemble (YOLOv5, Swin, Co-DETR) | Standardized 4 structural damage categories (D00, D10, D20, D40) | F1: ~78.2% (Ensemble) | < 5 FPS (Heavy ensemble) | Ensembles too slow and resource-heavy for real-time edge deployment. |
| **4** | **Du et al. (2020)**<br>*EURASIP JASP* | Pavement Distress (Custom) | YOLO-complex | Feature pyramid multi-scale fusion for non-standard crack aspects | mAP@0.5: 73.64% | 35 FPS (GPU) | Fixed anchor box clustering failed on oblique, zig-zag cracks. |
| **5** | **Wang et al. (2022)**<br>*Sensors* | RDD2020 subset | YOLOv7 + Coordinate Attention + BiFPN | Direction-aware attention mechanism to prevent crack feature dilution | mAP@0.5: 64.9% (+4.2% over YOLOv7) | 42 FPS (GPU) | Complex attention modules increased training latency and parameter size. |
| **6** | **Guan et al. (2021)**<br>*CACAIE* | PCNet 3D Stereo Dataset | Deep Pavement Crack Net (Stereo) | 3D depth and disparity estimation for pothole volumetric profiling | Pixel F1: 81.3% | 4 FPS | Requires calibrated dual-stereo cameras; unfeasible for smartphone crowdsourcing. |
| **7** | **RoadGuard (This Work)** | **RDD2022 (Standard 4-class)** | **Anchor-free YOLOv8 + P2 Neck + RDSI Engine** | **Lightweight edge inference, P2 feature map for micro-cracks, and Road Damage Severity Index (RDSI)** | **mAP@0.5: 67.4% (Single model)** | **~38 ms (M2 CPU) / 8 ms (CUDA)** | Bounding boxes approximate surface area rather than true millimeter 3D depth. |

