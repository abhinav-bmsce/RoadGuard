"""
RoadGuard - Multi-Domain Dataset Combiner & Kaggle Ingestion Engine
===================================================================
Integrates the RDD2022 Road Damage Dataset with the Lorenzo Arcioni Kaggle Dataset:
'Road Damage Dataset: Potholes, Cracks and Manholes'
(Kaggle: lorenzoarcioni/road-damage-dataset-potholes-cracks-and-manholes)
Published in: Nature Scientific Reports (2026), DOI: 10.1038/s41598-026-46679-4

Scientific Integrity & Taxonomy Compliance:
  RoadGuard Canonical 4-Class Taxonomy:
    0: D00_Longitudinal_Crack
    1: D10_Transverse_Crack
    2: D20_Alligator_Crack
    3: D40_Pothole

Strict Ingestion Rules:
  1. Map potholes (Arcioni Class 0) -> Canonical Class 3 (D40_Pothole) only when explicitly annotated.
  2. Generic cracks (Arcioni Class 1) are EXCLUDED from 4-class mapping because the Arcioni dataset
     aggregates all crack morphologies into a single bucket. Automatically mapping generic cracks
     to D00/D10/D20 would contaminate fine-grained crack decision boundaries.
  3. Incomplete Annotation Safeguard: Images containing excluded generic cracks are NOT retained
     with partial annotations, preventing unannotated cracks from serving as negative training examples.
  4. Manholes (Arcioni Class 2): Handled as non-damage infrastructure. Pure manhole images (no pavement
     damage) serve as verified negative background frames to suppress false-positive pothole detections.
  5. Deduplication: MD5 image byte hashing eliminates sequential video redundancies from vehicle dashcams
     and prevents train/val data leakage.
  6. Original RDD2022 dataset and active model weights are strictly preserved.
"""

import os
import shutil
import hashlib
import random
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any

try:
    import yaml
except ImportError:
    yaml = None


CANONICAL_CLASSES = {
    0: "D00_Longitudinal_Crack",
    1: "D10_Transverse_Crack",
    2: "D20_Alligator_Crack",
    3: "D40_Pothole"
}

ARCIONI_RAW_CLASSES = {
    0: "Pothole",
    1: "Crack",
    2: "Manhole"
}


def compute_file_hash(filepath: Path) -> str:
    """Computes MD5 hash of image bytes to detect identical or duplicate frames."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_yolo_bbox(parts: List[str]) -> Optional[Tuple[int, float, float, float, float]]:
    """
    Validates normalized YOLO bounding box coordinates.
    Returns: (cls_id, x_center, y_center, width, height) clamped to [0.001, 0.999] or None if degenerate.
    """
    if len(parts) < 5:
        return None
    try:
        cls_id = int(parts[0])
        x_c = float(parts[1])
        y_c = float(parts[2])
        w = float(parts[3])
        h = float(parts[4])
    except ValueError:
        return None

    # Sanity checks
    if w <= 0.0 or h <= 0.0:
        return None
    if x_c < -0.05 or x_c > 1.05 or y_c < -0.05 or y_c > 1.05:
        return None

    # Clamp to valid normalized domain [0.001, 0.999]
    x_c = max(0.001, min(0.999, x_c))
    y_c = max(0.001, min(0.999, y_c))
    w = max(0.001, min(0.999, w))
    h = max(0.001, min(0.999, h))

    return cls_id, x_c, y_c, w, h


def inspect_arcioni_dataset(raw_dir: Path) -> Dict[str, Any]:
    """
    Performs comprehensive census of the Lorenzo Arcioni Kaggle dataset.
    Returns dictionary with image counts, annotation distributions, and breakdown.
    """
    stats = {
        "total_images_found": 0,
        "total_labels_found": 0,
        "images_with_potholes": 0,
        "images_with_cracks": 0,
        "images_with_manholes": 0,
        "images_potholes_only": 0,
        "images_cracks_only": 0,
        "images_manholes_only": 0,
        "images_mixed": 0,
        "annotations_per_class": {0: 0, 1: 0, 2: 0},
        "duplicate_images_detected": 0,
        "unique_images": 0
    }

    seen_hashes: Set[str] = set()
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}

    # Search for all images in raw directory (recursively)
    image_paths = [p for p in raw_dir.rglob("*.*") if p.suffix.lower() in valid_exts]
    stats["total_images_found"] = len(image_paths)

    for img_p in image_paths:
        f_hash = compute_file_hash(img_p)
        if f_hash in seen_hashes:
            stats["duplicate_images_detected"] += 1
            continue
        seen_hashes.add(f_hash)

        # Look for corresponding label file (.txt)
        # Check adjacent or in labels/ directory
        lbl_p = img_p.with_suffix(".txt")
        if not lbl_p.exists():
            # Check parallel labels directory
            parts = list(img_p.parts)
            if "images" in parts:
                idx = len(parts) - 1 - parts[::-1].index("images")
                parts[idx] = "labels"
                cand = Path(*parts).with_suffix(".txt")
                if cand.exists():
                    lbl_p = cand

        if not lbl_p.exists():
            continue

        stats["total_labels_found"] += 1
        classes_in_image = set()

        with open(lbl_p, "r") as f:
            for line in f:
                parts = line.strip().split()
                validated = validate_yolo_bbox(parts)
                if validated:
                    cls_id, _, _, _, _ = validated
                    if cls_id in stats["annotations_per_class"]:
                        stats["annotations_per_class"][cls_id] += 1
                        classes_in_image.add(cls_id)

        has_pothole = 0 in classes_in_image
        has_crack = 1 in classes_in_image
        has_manhole = 2 in classes_in_image

        if has_pothole:
            stats["images_with_potholes"] += 1
        if has_crack:
            stats["images_with_cracks"] += 1
        if has_manhole:
            stats["images_with_manholes"] += 1

        if has_pothole and not has_crack and not has_manhole:
            stats["images_potholes_only"] += 1
        elif has_crack and not has_pothole and not has_manhole:
            stats["images_cracks_only"] += 1
        elif has_manhole and not has_pothole and not has_crack:
            stats["images_manholes_only"] += 1
        elif len(classes_in_image) > 1:
            stats["images_mixed"] += 1

    stats["unique_images"] = len(seen_hashes)
    return stats


def process_arcioni_subset(
    raw_dir: Path,
    output_train_imgs: Path,
    output_train_lbls: Path,
    output_val_imgs: Path,
    output_val_lbls: Path,
    val_ratio: float = 0.15,
    include_manholes_as_negative: bool = True,
    seed: int = 42
) -> Dict[str, int]:
    """
    Ingests compatible images and annotations from Lorenzo Arcioni dataset:
      - Class 0 (Pothole) -> Canonical Class 3 (D40_Pothole)
      - Class 1 (Crack) -> OMITTED (to preserve fine-grained D00/D10/D20 crack taxonomy)
      - Images with Class 1 -> EXCLUDED from training to prevent negative crack bias
      - Class 2 (Manhole) -> Pure manhole frames included as clean background images (if enabled)
    """
    random.seed(seed)
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}
    seen_hashes: Set[str] = set()

    summary = {
        "pothole_images_ingested": 0,
        "pothole_annotations_mapped": 0,
        "manhole_background_images_ingested": 0,
        "generic_crack_images_excluded": 0,
        "duplicate_images_skipped": 0,
        "train_images_added": 0,
        "val_images_added": 0,
    }

    image_paths = sorted([p for p in raw_dir.rglob("*.*") if p.suffix.lower() in valid_exts])

    for img_p in image_paths:
        # Check duplicate
        f_hash = compute_file_hash(img_p)
        if f_hash in seen_hashes:
            summary["duplicate_images_skipped"] += 1
            continue
        seen_hashes.add(f_hash)

        # Locate label
        lbl_p = img_p.with_suffix(".txt")
        if not lbl_p.exists():
            parts = list(img_p.parts)
            if "images" in parts:
                idx = len(parts) - 1 - parts[::-1].index("images")
                parts[idx] = "labels"
                cand = Path(*parts).with_suffix(".txt")
                if cand.exists():
                    lbl_p = cand

        if not lbl_p.exists():
            continue

        pothole_bboxes: List[Tuple[float, float, float, float]] = []
        has_generic_crack = False
        has_manhole = False

        with open(lbl_p, "r") as f:
            for line in f:
                parts = line.strip().split()
                validated = validate_yolo_bbox(parts)
                if not validated:
                    continue
                cls_id, x_c, y_c, w, h = validated
                if cls_id == 0:  # Pothole
                    pothole_bboxes.append((x_c, y_c, w, h))
                elif cls_id == 1:  # Generic crack
                    has_generic_crack = True
                elif cls_id == 2:  # Manhole
                    has_manhole = True

        # STRICT FILTERING RULE (Requirements 6, 7 & 8):
        # If an image contains generic cracks (Class 1), we MUST EXCLUDE IT from 4-class training.
        # Why? Because we cannot reliably distinguish D00 vs D10 vs D20 from generic crack labels,
        # and stripping the crack label while keeping the pothole would train the model to treat
        # unannotated cracks as negative background, harming crack recall in production.
        if has_generic_crack:
            summary["generic_crack_images_excluded"] += 1
            continue

        # Split determination (deterministic per file hash)
        is_val = (int(f_hash[:4], 16) / 65535.0) < val_ratio
        dst_img_dir = output_val_imgs if is_val else output_train_imgs
        dst_lbl_dir = output_val_lbls if is_val else output_train_lbls

        # Case A: Image contains confirmed potholes (and no unannotated generic cracks)
        if pothole_bboxes:
            dst_img_name = f"arcioni_pothole_{img_p.name}"
            dst_lbl_name = f"arcioni_pothole_{img_p.stem}.txt"

            # Map class 0 -> canonical class 3 (D40_Pothole)
            yolo_lines = [f"3 {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n" for (x, y, w, h) in pothole_bboxes]

            shutil.copy2(img_p, dst_img_dir / dst_img_name)
            with open(dst_lbl_dir / dst_lbl_name, "w") as f:
                f.writelines(yolo_lines)

            summary["pothole_images_ingested"] += 1
            summary["pothole_annotations_mapped"] += len(pothole_bboxes)
            if is_val:
                summary["val_images_added"] += 1
            else:
                summary["train_images_added"] += 1

        # Case B: Pure manhole image (no cracks, no potholes) - provides negative background sample
        elif has_manhole and include_manholes_as_negative and not pothole_bboxes:
            dst_img_name = f"arcioni_manhole_bg_{img_p.name}"
            dst_lbl_name = f"arcioni_manhole_bg_{img_p.stem}.txt"

            shutil.copy2(img_p, dst_img_dir / dst_img_name)
            # Empty label file designates an explicit negative background frame in YOLOv8
            with open(dst_lbl_dir / dst_lbl_name, "w") as f:
                pass

            summary["manhole_background_images_ingested"] += 1
            if is_val:
                summary["val_images_added"] += 1
            else:
                summary["train_images_added"] += 1

    return summary


def build_unified_roadguard_dataset(
    rdd2022_root: Path,
    arcioni_root: Path,
    output_root: Path,
    val_ratio: float = 0.15
) -> Dict[str, Any]:
    """
    Creates a unified training and validation dataset combining:
      1. RDD2022 multi-country benchmark (classes 0, 1, 2, 3)
      2. Lorenzo Arcioni Kaggle dataset (explicit D40 potholes + manhole negative background frames)
    Generates data.yaml configured for YOLOv8 training.
    """
    print(f"\n=======================================================")
    print(f"RoadGuard Dataset Expansion & Ingestion Engine")
    print(f"Target Directory: {output_root}")
    print(f"=======================================================\n")

    train_img = output_root / "train" / "images"
    train_lbl = output_root / "train" / "labels"
    val_img = output_root / "val" / "images"
    val_lbl = output_root / "val" / "labels"

    for d in [train_img, train_lbl, val_img, val_lbl]:
        d.mkdir(parents=True, exist_ok=True)

    results = {}

    # 1. Ingest Baseline RDD2022 (Identity mapping: 0->0, 1->1, 2->2, 3->3)
    if rdd2022_root.exists():
        print(f"[*] Ingesting Baseline RDD2022 Dataset from: {rdd2022_root}")
        rdd_train_imgs = rdd2022_root / "train" / "images"
        rdd_train_lbls = rdd2022_root / "train" / "labels"
        rdd_val_imgs = rdd2022_root / "val" / "images"
        rdd_val_lbls = rdd2022_root / "val" / "labels"

        rdd_train_count = 0
        rdd_val_count = 0

        if rdd_train_imgs.exists():
            for p in rdd_train_imgs.glob("*.*"):
                shutil.copy2(p, train_img / f"rdd_{p.name}")
                lbl = rdd_train_lbls / f"{p.stem}.txt"
                if lbl.exists():
                    shutil.copy2(lbl, train_lbl / f"rdd_{p.stem}.txt")
                rdd_train_count += 1

        if rdd_val_imgs.exists():
            for p in rdd_val_imgs.glob("*.*"):
                shutil.copy2(p, val_img / f"rdd_val_{p.name}")
                lbl = rdd_val_lbls / f"{p.stem}.txt"
                if lbl.exists():
                    shutil.copy2(lbl, val_lbl / f"rdd_val_{p.stem}.txt")
                rdd_val_count += 1

        print(f"    RDD2022 Ingested: {rdd_train_count} train images, {rdd_val_count} val images.")
        results["rdd2022_train_images"] = rdd_train_count
        results["rdd2022_val_images"] = rdd_val_count

    # 2. Ingest Lorenzo Arcioni Kaggle Dataset
    if arcioni_root.exists():
        print(f"\n[*] Inspecting & Ingesting Lorenzo Arcioni Kaggle Dataset from: {arcioni_root}")
        census = inspect_arcioni_dataset(arcioni_root)
        print(f"    Total Images Found: {census['total_images_found']} (Unique: {census['unique_images']})")
        print(f"    Annotations Census:")
        print(f"      - Potholes (Class 0): {census['annotations_per_class'][0]}")
        print(f"      - Cracks (Class 1)  : {census['annotations_per_class'][1]} [EXCLUDED from 4-class mapping]")
        print(f"      - Manholes (Class 2): {census['annotations_per_class'][2]} [Infrastructure Negative Class]")

        arcioni_summary = process_arcioni_subset(
            raw_dir=arcioni_root,
            output_train_imgs=train_img,
            output_train_lbls=train_lbl,
            output_val_imgs=val_img,
            output_val_lbls=val_lbl,
            val_ratio=val_ratio,
            include_manholes_as_negative=True
        )
        print(f"\n    Arcioni Ingestion Results:")
        print(f"      - Pothole Images Ingested        : {arcioni_summary['pothole_images_ingested']}")
        print(f"      - D40 Pothole Annotations Mapped : {arcioni_summary['pothole_annotations_mapped']}")
        print(f"      - Manhole Backgrounds Ingested   : {arcioni_summary['manhole_background_images_ingested']}")
        print(f"      - Generic Crack Images Excluded  : {arcioni_summary['generic_crack_images_excluded']}")
        print(f"      - Duplicate Images Skipped       : {arcioni_summary['duplicate_images_skipped']}")
        results["arcioni_summary"] = arcioni_summary

    # 3. Create Canonical data.yaml
    yaml_file = output_root / "data.yaml"
    if yaml is not None:
        data_yaml_dict = {
            "path": str(output_root.resolve()),
            "train": "train/images",
            "val": "val/images",
            "nc": 4,
            "names": CANONICAL_CLASSES
        }
        with open(yaml_file, "w") as f:
            yaml.dump(data_yaml_dict, f, default_flow_style=False)
    else:
        # Dependency-free YAML writing
        lines = [
            f"path: {output_root.resolve()}",
            "train: train/images",
            "val: val/images",
            "nc: 4",
            "names:",
        ]
        for k, v in CANONICAL_CLASSES.items():
            lines.append(f"  {k}: {v}")
        with open(yaml_file, "w") as f:
            f.write("\n".join(lines) + "\n")

    total_train = len(list(train_img.glob("*.*")))
    total_val = len(list(val_img.glob("*.*")))
    print(f"\n[+] Unified Dataset Created Successfully!")
    print(f"    data.yaml saved at: {yaml_file}")
    print(f"    Total Combined Training Images  : {total_train}")
    print(f"    Total Combined Validation Images: {total_val}")

    results["total_train"] = total_train
    results["total_val"] = total_val
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RoadGuard Dataset Combiner & Kaggle Ingestion")
    parser.add_argument("--rdd", type=Path, default=Path("ml/dataset/processed"), help="RDD2022 processed directory")
    parser.add_argument("--arcioni", type=Path, default=Path("ml/dataset/arcioni_raw"), help="Lorenzo Arcioni raw dataset directory")
    parser.add_argument("--output", type=Path, default=Path("ml/dataset/roadguard_unified"), help="Output directory")
    parser.add_argument("--inspect-only", action="store_true", help="Only perform census inspection")
    args = parser.parse_args()

    if args.inspect_only and args.arcioni.exists():
        census = inspect_arcioni_dataset(args.arcioni)
        if yaml is not None:
            print(yaml.dump(census, default_flow_style=False))
        else:
            import json
            print(json.dumps(census, indent=2))
    else:
        build_unified_roadguard_dataset(args.rdd, args.arcioni, args.output)
