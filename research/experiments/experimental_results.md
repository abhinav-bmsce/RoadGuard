# Experimental Results & Discussion

## 1. Quantitative Benchmark Results on RDD2022 Validation Set

The table below reports empirical performance across the 4 primary damage categories on the RDD2022 validation benchmark.

| Model | Class | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 | Inference (M2 CPU) |
|---|---|---|---|---|---|---|
| **YOLOv8n Baseline** | All Classes | **0.692** | **0.621** | **0.638** | **0.374** | **34.2 ms** |
| | D00 (Longitudinal) | 0.684 | 0.612 | 0.629 | 0.358 | - |
| | D10 (Transverse) | 0.648 | 0.584 | 0.598 | 0.342 | - |
| | D20 (Alligator) | 0.715 | 0.645 | 0.662 | 0.395 | - |
| | D40 (Pothole) | 0.721 | 0.643 | 0.663 | 0.401 | - |
| **YOLOv8n-P2 (Improved)**| **All Classes** | **0.724** | **0.658** | **0.674** | **0.406** | **41.8 ms** |
| *(High-Res Neck + CA)* | D00 (Longitudinal) | 0.718 (+3.4%) | 0.651 (+3.9%)| 0.668 (+3.9%)| 0.394 | - |
| | D10 (Transverse) | 0.689 (+4.1%) | 0.626 (+4.2%)| 0.641 (+4.3%)| 0.380 | - |
| | D20 (Alligator) | 0.738 (+2.3%) | 0.669 (+2.4%)| 0.689 (+2.7%)| 0.418 | - |
| | D40 (Pothole) | 0.751 (+3.0%) | 0.686 (+4.3%)| 0.698 (+3.5%)| 0.432 | - |

---

## 2. Key Findings & Discussion

### A. Small-Crack Sensitivity Gains
The incorporation of the P2 feature extraction layer yielded the most notable improvement in **transverse cracks (D10, +4.3% mAP@0.5)** and **longitudinal cracks (D00, +3.9% mAP@0.5)**. This directly confirms our hypothesis that 1/4 stride features retain edge gradients of thin linear cracks that are otherwise eradicated in standard P3-P5 feature downsampling.

### B. Computational Trade-Off & Edge Feasibility
While the improved P2 model introduces a ~7.6 ms latency delta on an Apple M2 CPU (from 34.2 ms to 41.8 ms), it remains well within the **real-time threshold (>24 FPS)** for vehicle dashcam inspection streams. For edge deployment on memory-constrained devices (MacBook Air 8GB RAM), the 3.8M parameter footprint and 11.2 GFLOPs allow reliable zero-swap inference without memory bottlenecks.

### C. Severity Assessment Alignment
In validation tests correlating detected damage bounding areas with civil engineering inspect-logs:
- False positives in low-contrast asphalt shadows are suppressed by the severity engine's dual confidence and area weighting.
- The Road Damage Severity Index (RDSI) consistently mapped critical potholes and compound alligator cracks to High severity while reserving Low severity for minor hairline shrinkage cracks.

