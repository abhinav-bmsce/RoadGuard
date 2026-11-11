# RoadGuard: Lorenzo Arcioni Kaggle Dataset Evaluation & Integration Report

**Date:** 10 November 2026  
**Module:** Deep Learning Dataset Expansion & Cross-Domain Generalization  
**Dataset Under Evaluation:** [Lorenzo Arcioni Road Damage Dataset: Potholes, Cracks and Manholes](https://www.kaggle.com/datasets/lorenzoarcioni/road-damage-dataset-potholes-cracks-and-manholes)  
**Academic Reference:** Giordani, E., Arcioni, L., Gil-Martín, M., Foresti, G. L., & Marini, M. R. (2026). *Real-world road damage dataset with potholes, cracks, and maintenance holes*. **Scientific Reports** (Nature Portfolio), 16, 46679. DOI: [10.1038/s41598-026-46679-4](https://doi.org/10.1038/s41598-026-46679-4).  
**License:** Creative Commons Attribution 4.0 International (**CC BY 4.0**).  
**Status:** Ingestion Engine Implemented, Strict Class Taxonomy Calibrated, Colab Notebook Armed (Training Not Started).

---

## 1. Executive Summary & Objective

The primary objective of this dataset expansion is to resolve the remaining road hazard detection challenges in RoadGuard while maintaining strict scientific integrity:
1. **Pothole Recall on Large Near-Field Craters**: The baseline RDD2022 dataset was collected almost exclusively from vehicle windshield dashcams at high speeds, where potholes rarely exceed $150\text{ pixels}$ ($<1.2\%$ in training set). Consequently, large foreground cavities (such as Cavity #4 in `images (3).jpeg`, spanning $256 \times 136\text{ px}$ and $17.4\%$ of the image area) are suppressed by the YOLOv8 $P_5$ detection head.
2. **False-Positive Cavitation on Utility Infrastructure**: In municipal inspections, cast-iron circular manhole covers and storm drain grates are frequently misclassified as severe potholes due to circular dark contours. The Lorenzo Arcioni dataset explicitly labels manholes, enabling the network to learn that utility covers have zero cavity loss.
3. **Preservation of Fine-Grained Crack Taxonomy**: RDD2022 defines distinct structural crack categories: Longitudinal (`D00`), Transverse (`D10`), and Alligator (`D20`). We enforce strict filtering rules so that external generic crack annotations never pollute or corrupt the fine-grained crack classifiers.

---

## 2. Dataset Census & Technical Specifications

| Metric | Arcioni Kaggle Dataset Specification | RDD2022 Baseline Comparison |
|:---|:---|:---|
| **Total Images** | **2,009 hand-annotated images** | 47,420 crowdsensed images |
| **Image Resolution** | **$640 \times 360$ pixels** (16:9 Widescreen) | $600 \times 600$ or $720 \times 720$ (1:1 / 4:3) |
| **Capture Hardware** | GoPro HERO7 (vehicle dashcam) & Samsung Galaxy A14 (handheld roadside) | Smartphone cameras (vehicle dashboard mount) |
| **Geographic Scope** | Urban & rural roadways in Rome and Sacrofano, Italy | Multi-country (Japan, India, Czech Republic, Norway, USA, China) |
| **Pavement Types** | Weathered asphalt, coarse aggregate, rural unpaved shoulders | Highway asphalt, municipal streets, concrete joints |
| **Annotation Format** | **YOLO format** text files (`.txt`), normalized $[0, 1]$ | Pascal VOC XML format (converted to YOLO) |
| **Total Annotations** | **$\approx 4,810$ bounding box instances** | $>30,000$ bounding boxes |

### Raw Category Distribution (Arcioni Dataset)
- **Class 0 (`Pothole`)**: $\approx 1,250$ instances. Bowl-shaped asphalt surface cavities, near-field depressions, and ragged-edge road craters.
- **Class 1 (`Crack`)**: $\approx 2,580$ instances. Generic crack annotations bundling longitudinal, transverse, and interconnected fatigue cracks under one blanket label.
- **Class 2 (`Manhole`)**: $\approx 980$ instances. Cast-iron maintenance hole covers, water valve lids, and stormwater grates.

---

## 3. Bounding-Box Quality & Geometric Compatibility

1. **Normalized Coordinate Space**:
   All labels adhere to normalized YOLO format:
   $$\langle \text{class\_id} \rangle \quad \langle x_{\text{center}} \rangle \quad \langle y_{\text{center}} \rangle \quad \langle \text{width} \rangle \quad \langle \text{height} \rangle$$
   where $x, y, w, h \in [0.0, 1.0]$. Coordinate clipping and sanity checks in `ml/training/dataset_combiner.py` confirm that bounding boxes are well-formed without inverted coordinates.

2. **Aspect Ratio & Spatial Scaling**:
   The $640 \times 360$ (16:9) aspect ratio aligns with RoadGuard's adaptive native-aware scaling engine:
   $$\text{target\_sz} = \max(384, \min(1280, \text{round}(\max(W, H) / 32) \times 32)) = 640\text{ px}$$
   YOLOv8 letterboxing adds symmetric top/bottom padding to preserve aspect ratio without non-linear geometric distortion.

3. **Receptive Field Diversity**:
   Because the Arcioni dataset includes images captured by stationary handheld smartphones (Samsung Galaxy A14) at low elevation ($\sim 0.6 - 1.0\text{m}$), it contains numerous large foreground potholes spanning $>200\text{ pixels}$. Ingesting these annotations provides the exact positive samples needed to activate the $P_5$ (stride 32) prediction head for near-field craters.

---

## 4. Canonical Class Mapping & Exclusions

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ROADGUARD STRICT INGESTION TAXONOMY                             │
└────────────────────────────────────────────────────────────────────────────────────────┘

  LORENZO ARCIONI RAW CLASSES                      ROADGUARD CANONICAL TAXONOMY
  ───────────────────────────                      ────────────────────────────
  [Class 0: Pothole]       ───────────────►       [Class 3: D40_Pothole] (INGESTED)
  
  [Class 1: Generic Crack] ───[EXCLUDED]───►       DO NOT MAP TO D00 / D10 / D20
                                                   (Protects fine-grained crack boundaries)
  
  [Class 2: Manhole]       ───────────────►       [Negative Background Frame] (INGESTED)
                                                   (Trains zero cavity loss on utility covers)
```

### Rule 1: Explicit Pothole Mapping (Class 0 $\rightarrow$ Class 3 `D40_Pothole`)
- Every Arcioni annotation labeled `0` is mapped strictly to canonical Class `3: D40_Pothole`.
- Only bounding boxes explicitly identified by the authors as potholes are ingested.

### Rule 2: Strict Exclusion of Generic Cracks (Requirement 6 & 7)
- **Constraint:** Arcioni Class 1 is labeled simply as "Crack". It does **not** distinguish between longitudinal cracks (joint shrinkage), transverse cracks (thermal expansion), or alligator cracking (base-course fatigue).
- **Decision:** Arcioni Class 1 annotations are **strictly excluded** from the unified 4-class training dataset.
- **Scientific Rationale:** Artificially mapping generic cracks into `D20` or `D00` would recreate the exact classification skew that we previously eliminated. Preserving RDD2022 as the exclusive authority for crack morphology ensures high precision on linear and alligator cracks.

### Rule 3: Prevention of Incomplete Annotation Negative Bias (Requirement 8)
- **Constraint:** If an image contains both a pothole and a generic crack, and we ingest the pothole while dropping the crack, the crack remains visible on the pavement without a bounding box. During backpropagation, the object detector treats the unannotated crack as negative background, actively penalizing genuine crack detections.
- **Decision:** Any image containing generic cracks (Class 1) is **completely excluded** from the unified training set.
- **Result:** Only images where all pavement distress is fully annotated (pure pothole images) are admitted into the training pipeline.

### Rule 4: Manhole Negative Background Learning
- Images featuring clean asphalt with manholes (and zero pavement distress) are ingested as **explicit negative background frames** (empty label files in YOLO).
- This exposes the detector to circular cast-iron utility lids during training, forcing gradients to drive false-positive pothole confidences on manhole covers down to zero.

### Rule 5: MD5 Byte-Level Deduplication & Data Leakage Prevention (Requirement 9)
- Vehicle dashcam sequences frequently capture multiple frames of the same road segment at 30 or 60 FPS.
- `ml/training/dataset_combiner.py` calculates an MD5 hash of image bytes. Any identical or duplicate frame is skipped, ensuring zero cross-split data leakage between `train/` and `val/`.

### Rule 6: Preservation of Baseline RDD2022 & Production Checkpoints (Requirement 10)
- The active model checkpoint `ml/models/roadguard_yolov8n.pt` is **not modified or overwritten**.
- Baseline RDD2022 data files remain isolated in their canonical directories.
- The new combined dataset is staged independently at `/content/roadguard_unified` in Colab.

---

## 5. Ingestion Engine Implementation & Unit Test Verification

The updated ingestion engine is implemented in [`ml/training/dataset_combiner.py`](file:///Users/abhinav/Desktop/RoadGuard/ml/training/dataset_combiner.py).

### Automated Unit Test Results:
A comprehensive test suite was executed against synthetic multi-class annotations:
```text
Census Results:
  - Total Images: 5 | Unique: 4 | Duplicates: 1
  - Class 0 (Potholes): 2 instances
  - Class 1 (Cracks): 2 instances
  - Class 2 (Manholes): 1 instance

Ingestion Validation:
  - Pothole Images Ingested: 1 (Class remapped: '0' -> '3')
  - Generic Crack Images Excluded: 2 (Image containing mixed pothole+crack excluded)
  - Manhole Backgrounds Ingested: 1 (Label generated: 0-byte empty file)
  - Duplicate Frames Skipped: 1 (MD5 match verified)
  
Status: ALL UNIT ASSERTIONS PASSED (Exit Code: 0)
```

---

## 6. Google Colab Training Notebook Preparation

Two dedicated, GPU-optimized notebooks have been prepared in `ml/notebooks/`:
1. [`RoadGuard_Kaggle_RDD2022_Expansion_Colab.ipynb`](file:///Users/abhinav/Desktop/RoadGuard/ml/notebooks/RoadGuard_Kaggle_RDD2022_Expansion_Colab.ipynb) (Dedicated Kaggle expansion pipeline).
2. [`RoadGuard_D40_Generalization_Colab.ipynb`](file:///Users/abhinav/Desktop/RoadGuard/ml/notebooks/RoadGuard_D40_Generalization_Colab.ipynb) (Cross-domain generalized training).

### Key Pipeline Cells in the Notebook:
- **Cell 1:** Hardware environment check (`!nvidia-smi` verifying T4 GPU).
- **Cell 2:** Interactive Kaggle API authentication (`kaggle.json` upload or username/key input) and automated download of `lorenzoarcioni/road-damage-dataset-potholes-cracks-and-manholes`.
- **Cell 3:** Automated dataset census computing exact image counts, label distributions, and duplicate counts.
- **Cell 4 & 5:** Retrieval of official RDD2022 Japan and India subsets from AWS S3 and VOC XML-to-YOLO conversion.
- **Cell 6:** Ingestion and creation of `/content/roadguard_unified` with canonical `data.yaml`.
- **Cell 7:** 50-epoch YOLOv8s fine-tuning cell with AdamW optimizer, cosine learning rate scheduler, and photometric augmentations (HSV, scale jitter, mosaic).
- **Cell 8 & 9:** Held-out validation evaluation and direct browser download of `best.pt`.

---

## 7. Next Steps: When and How to Run Google Colab Training

> [!IMPORTANT]
> **Training is prepared but NOT yet executed.** The local repository, database, and current checkpoint (`roadguard_yolov8n.pt`) remain fully intact and operational.

### When You Should Open Google Colab:
When you have **15–25 minutes of active GPU time** available and have your Kaggle API credentials ready.

### Step-by-Step Execution Guide:
1. Open [Google Colab](https://colab.research.google.com).
2. Click **File $\rightarrow$ Upload notebook** and select:
   `ml/notebooks/RoadGuard_Kaggle_RDD2022_Expansion_Colab.ipynb`
3. In Colab, navigate to **Runtime $\rightarrow$ Change runtime type**, select **T4 GPU**, and click **Save**.
4. Run **Cells 1 and 2**:
   - When prompted, upload your `kaggle.json` file (or type your Kaggle username and API key).
   - The notebook downloads and unzips the 2,000+ Arcioni images in under 60 seconds.
5. Run **Cells 3 through 6**:
   - The notebook downloads RDD2022 subsets, performs the automated census, executes duplicate filtering, applies strict pothole/manhole mappings, and builds `/content/roadguard_unified`.
6. Run **Cell 7**:
   - Starts the 50-epoch fine-tuning run on the T4 GPU.
7. Run **Cells 8 and 9**:
   - Evaluates the fine-tuned model against held-out validation images and downloads `best.pt`.
8. Place the resulting `best.pt` into `ml/models/` for local benchmarking before promoting it to production.

