# Experimental Setup & Protocol

## 1. Hardware & Computational Environment
- **Training Environment**: Google Colab Pro GPU (NVIDIA Tesla T4 / V100 16GB VRAM, CUDA 12.2, PyTorch 2.x).
- **Target Inference Environment**: Apple Silicon M2 (8-core CPU, 10-core GPU, 8GB Unified RAM, macOS 14+), using PyTorch MPS and CPU execution.

## 2. Dataset Preparation & Partitioning
- **Primary Source**: RDD2022 (Crowdsensing-based Road Damage Detection Challenge 2022).
- **Country Subsets**: Multi-country benchmark balancing Japan, India, and Czech Republic road surface diversity.
- **Classes**:
  - `0`: D00 - Longitudinal Crack
  - `1`: D10 - Transverse Crack
  - `2`: D20 - Alligator Crack
  - `3`: D40 - Pothole
- **Splits**:
  - Training: 70%
  - Validation: 15%
  - Test / Benchmark: 15%
  - Stratification applied to ensure equal relative proportion of minority class D40 (potholes) across splits.

## 3. Training Hyperparameters

| Hyperparameter | Baseline Configuration | Improved Configuration (P2 Feature Layer) |
|---|---|---|
| Model Architecture | YOLOv8n (Standard P3-P5) | YOLOv8n-P2 (High-Res Neck) |
| Epochs | 100 (Early stopping patience = 15) | 100 (Early stopping patience = 15) |
| Batch Size | 32 (Colab GPU) | 16 (Due to $160 \times 160$ feature maps) |
| Image Resolution | $640 \times 640$ | $640 \times 640$ |
| Optimizer | AdamW | AdamW |
| Initial Learning Rate ($lr_0$) | 0.001 | 0.001 |
| Final Learning Rate ($lr_f$) | 0.01 ($lr_0 \times 0.01$) | 0.01 ($lr_0 \times 0.01$) |
| Cosine Annealing | Yes | Yes |
| Weight Decay | 0.0005 | 0.0005 |
| Box Loss Gain ($\lambda_{box}$) | 7.5 | 7.5 |
| Class Loss Gain ($\lambda_{cls}$) | 0.5 | 0.5 |
| DFL Loss Gain ($\lambda_{dfl}$) | 1.5 | 1.5 |
| Mosaic Augmentation | Enabled (first 90 epochs) | Enabled (first 90 epochs) |

## 4. Evaluation Metrics
1. **Precision ($P$)**: Ratio of true detected road damage instances to total predicted damages.
2. **Recall ($R$)**: Fraction of ground-truth distress instances successfully detected.
3. **mAP@0.5**: Mean Average Precision at an Intersection-over-Union (IoU) threshold of 0.50 (official CRDDC benchmark metric).
4. **mAP@0.5:0.95**: Mean Average Precision averaged across IoU thresholds from 0.50 to 0.95 in 0.05 increments.
5. **Inference Latency (ms)**: End-to-end forward pass + post-processing (NMS) latency measured over 500 test images.

