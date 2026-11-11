# RDD2022 Dataset Guide

## 1. Overview & Source
The **Crowdsensing-based Road Damage Detection Challenge (CRDDC 2022)** dataset, curated by Sekilab (University of Tokyo) and Maeda et al., contains 47,420 multi-country road pavement surface images collected via smartphone cameras mounted on vehicle windshields.

- **Official Publication**: Arya, D., et al. (2022). *Crowdsensing-based Road Damage Detection Challenge (CRDDC'2022)*. IEEE BigData. DOI: [10.1109/BigData55660.2022.10020475](https://doi.org/10.1109/BigData55660.2022.10020475).
- **Official Repository**: [GitHub: sekilab/RoadDamageDetector](https://github.com/sekilab/RoadDamageDetector)

---

## 2. Standard Damage Categories

RoadGuard standardizes the 4 primary structural pavement distress categories:

| Class Code | Category Name | Description | Annotation Key |
|---|---|---|---|
| **D00** | Longitudinal Crack | Cracks running parallel to the direction of vehicular travel (joint shrinkage) | `0` |
| **D10** | Transverse Crack | Cracks running perpendicular to travel (thermal stresses) | `1` |
| **D20** | Alligator Crack | Intersecting fatigue crack networks (base structural failure) | `2` |
| **D40** | Pothole | Bowl-shaped surface cavities resulting from moisture freeze-thaw | `3` |

---

## 3. Data Preparation Pipeline

RoadGuard provides an automated preprocessing pipeline in `ml/dataset/`:

### Step 1: Download Subsets
```bash
python ml/dataset/download_rdd2022.py --country Japan --output ml/dataset/raw
```
*(In Google Colab, you can download India, Japan, or Czech subsets directly via AWS S3).*

### Step 2: Convert VOC XML to YOLO TXT
Raw annotations are distributed in Pascal VOC XML format:
```xml
<annotation>
  <filename>Japan_000120.jpg</filename>
  <size>
    <width>600</width>
    <height>600</height>
  </size>
  <object>
    <name>D00</name>
    <bndbox>
      <xmin>145</xmin>
      <ymin>220</ymin>
      <xmax>280</xmax>
      <ymax>510</ymax>
    </bndbox>
  </object>
</annotation>
```

Run the conversion script:
```bash
python ml/dataset/voc_to_yolo.py --xml_dir ml/dataset/raw/annotations/xmls --labels_dir ml/dataset/raw/labels
```

### Step 3: Stratified Splitting
```bash
python ml/dataset/split_dataset.py --images ml/dataset/raw/images --labels ml/dataset/raw/labels --output ml/dataset/processed
```
This produces the standard directory tree required by YOLOv8:
```
processed/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

