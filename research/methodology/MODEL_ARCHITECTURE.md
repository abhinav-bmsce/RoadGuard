# Model Architecture & Optimization Strategy

## 1. Architectural Foundations: YOLOv8 vs. Legacy YOLO
RoadGuard deploys a tailored YOLOv8 architecture optimized for real-time edge execution on Apple Silicon (M2 MPS / CPU) and resource-constrained civil inspection vehicles.

### Key Architectural Enhancements in RoadGuard:
1. **Decoupled Detection Head**:
   - In traditional YOLO models (YOLOv3 through YOLOv5), the classification score and bounding box regression coordinates were predicted from a single shared feature representation.
   - YOLOv8 separates the classification branch (BCE Loss) from the regression branch (Distribution Focal Loss + Complete IoU Loss). This decoupling dramatically reduces negative gradient interference during backpropagation, crucial when distinguishing between visually subtle crack classes (D00 vs D10).
2. **Anchor-Free Assignment (Task-Aligned Assigner)**:
   - Eliminates predefined anchor boxes. Cracks exhibit non-uniform aspect ratios that cluster poorly into static anchor boxes. The Task-Aligned Assigner dynamically computes a metric $t = s^\alpha \times \text{IoU}^\beta$ aligning classification score $s$ with bounding localization $\text{IoU}$.
3. **C2f (Cross Stage Partial with 2 Convolutions and Bottleneck)**:
   - Enhances gradient flow across stages while reducing computational latency.

---

## 2. Research Hypothesis: Mitigating Small Crack Feature Degradation

### Problem Statement
In standard feature pyramids (P3, P4, P5), the stride levels are 8, 16, and 32 pixels. For a 640x640 road input image:
- P3 corresponds to $80 \times 80$ feature resolution.
- A thin transverse crack of 2-3 pixel width loses spatial frequency information through successive downsamplings.

### Proposed Research Optimization: P2 Small-Object Detection Layer
By extracting features from stage 2 (stride 4, $160 \times 160$ feature resolution) and routing it via a lateral top-down pathway into the detection neck:
- The detector retains micro-crack edges and texture.
- Small crack recall is hypothesized to improve by $>3.5\%$ with a modest parameter increase (~12%).

```
Input (640x640)
       │
     Stem (Stride 2)
       │
    Stage 1 (Stride 2)
       │
    Stage 2 (Stride 4)  ────── Lateral Connection ──────> P2 Head (160x160) [Micro-Cracks]
       │                                                         │
    Stage 3 (Stride 8)  ────── Lateral Connection ──────> P3 Head (80x80)   [Medium Damage]
       │                                                         │
    Stage 4 (Stride 16) ────── Lateral Connection ──────> P4 Head (40x40)   [Large Potholes]
       │                                                         │
    Stage 5 (Stride 32) ────── Lateral Connection ──────> P5 Head (20x20)   [Broad Distress]
```

---

## 3. Data Augmentation Strategy for Road Surfaces
Road surface imagery suffers from extreme lighting variation, sun glares, asphalt dampness, and shadow occlusions (trees, roadside buildings, vehicle overhangs). Our augmentation pipeline applies:
- **Mosaic (p=1.0)**: Blends 4 disparate road views, teaching multi-scale crack detection.
- **Random HSV perturbation**: Hue $\pm 0.015$, Saturation $\pm 0.7$, Value $\pm 0.4$ (models shadow/glare).
- **Affine transformations**: Random rotation $\pm 10^\circ$, translation $\pm 10\%$, scale $\pm 50\%$.
- **MixUp (p=0.15)**: Helps regularize against ambiguous asphalt textures.

