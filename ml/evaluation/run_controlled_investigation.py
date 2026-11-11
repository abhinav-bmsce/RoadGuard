"""
RoadGuard - Controlled Model Accuracy & Classification Investigation
Compares the Original Model (COCO adapted) against the Corrected Fine-Tuned RDD2022 Model across:
- Known Pothole image (D40)
- Known Longitudinal Crack image (D00)
- Known Transverse Crack image (D10)
- Known Alligator Crack image (D20)
- Multiple genuine RDD2022 validation images

Saves:
- Original image
- Original model annotated prediction
- Corrected model annotated prediction
- Complete JSON log with Ground Truth, predicted class, confidence, and bounding box
"""

import json
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

ROADGUARD_TAXONOMY = {
    0: "D00_Longitudinal_Crack",
    1: "D10_Transverse_Crack",
    2: "D20_Alligator_Crack",
    3: "D40_Pothole"
}

COLOR_MAP = {
    0: (16, 185, 129),   # Emerald for D00
    1: (6, 182, 212),    # Cyan for D10
    2: (245, 158, 11),   # Amber for D20
    3: (239, 68, 68),    # Crimson for D40
}


def draw_boxes(image_path: Path, detections: list, out_path: Path, title: str):
    img = cv2.imread(str(image_path))
    h, w = img.shape[:2]

    # Draw detections
    for d in detections:
        c_id = d["class_id"]
        c_name = d["class_name"].split("_")[0]
        conf = d["confidence"]
        box = d["bbox"]
        color = COLOR_MAP.get(c_id, (255, 255, 255))

        x1, y1 = int(box["xmin"]), int(box["ymin"])
        x2, y2 = int(box["xmax"]), int(box["ymax"])

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f"{c_name} {conf*100:.0f}%"
        cv2.rectangle(img, (x1, max(0, y1 - 20)), (x1 + len(label) * 9 + 10, y1), color, -1)
        cv2.putText(img, label, (x1 + 4, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

    # Title header banner
    banner = np.zeros((32, w, 3), dtype=np.uint8)
    banner[:] = (15, 23, 42)
    cv2.putText(banner, f"{title} | Detections: {len(detections)}", (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    combined = np.vstack([banner, img])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), combined)


def run_investigation():
    print("=" * 70)
    print(" RoadGuard - Forensic Model Accuracy & Classification Investigation")
    print("=" * 70)

    orig_model = YOLO("ml/models/roadguard_yolov8n_original_coco.pt")
    corr_model = YOLO("ml/models/roadguard_yolov8n.pt")

    img_dir = Path("ml/evaluation/genuine_rdd2022")
    images = sorted(list(img_dir.glob("*.jpg")))
    print(f"Loaded {len(images)} genuine benchmark evaluation images from {img_dir}\n")

    full_report = {
        "evaluation_count": len(images),
        "results": []
    }

    class_stats_orig = {0: 0, 1: 0, 2: 0, 3: 0, "other": 0}
    class_stats_corr = {0: 0, 1: 0, 2: 0, 3: 0, "other": 0}
    gt_total_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for img_path in images:
        lbl_path = img_path.with_suffix(".txt")
        gt_annotations = []
        if lbl_path.exists():
            for line in lbl_path.read_text().strip().splitlines():
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    xc, yc, bw, bh = [float(x) for x in parts[1:5]]
                    # Convert normalized YOLO to pixel coords
                    img_sample = cv2.imread(str(img_path))
                    h, w = img_sample.shape[:2]
                    xmin = round((xc - bw / 2.0) * w, 2)
                    ymin = round((yc - bh / 2.0) * h, 2)
                    xmax = round((xc + bw / 2.0) * w, 2)
                    ymax = round((yc + bh / 2.0) * h, 2)
                    gt_annotations.append({
                        "class_id": cls_id,
                        "class_name": ROADGUARD_TAXONOMY.get(cls_id, f"Class_{cls_id}"),
                        "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
                    })
                    if cls_id in gt_total_counts:
                        gt_total_counts[cls_id] += 1

        # 1. Run Original Model
        orig_res = orig_model.predict(str(img_path), conf=0.25, verbose=False)[0]
        orig_dets = []
        for b in orig_res.boxes:
            raw_cls = int(b.cls[0].item())
            conf = round(float(b.conf[0].item()), 4)
            # Replicate previous backend bug behavior: raw_cls % 4
            mapped_cls = raw_cls % 4 if raw_cls not in ROADGUARD_TAXONOMY else raw_cls
            coords = b.xyxy[0].tolist()
            orig_dets.append({
                "raw_cls_id": raw_cls,
                "class_id": mapped_cls,
                "class_name": ROADGUARD_TAXONOMY[mapped_cls],
                "confidence": conf,
                "bbox": {"xmin": round(coords[0], 2), "ymin": round(coords[1], 2), "xmax": round(coords[2], 2), "ymax": round(coords[3], 2)}
            })
            if mapped_cls in class_stats_orig:
                class_stats_orig[mapped_cls] += 1
            else:
                class_stats_orig["other"] += 1

        # 2. Run Corrected Model
        corr_res = corr_model.predict(str(img_path), conf=0.25, verbose=False)[0]
        corr_dets = []
        img_h, img_w = orig_res.orig_shape
        for b in corr_res.boxes:
            raw_cls = int(b.cls[0].item())
            conf = round(float(b.conf[0].item()), 4)
            raw_name = corr_model.names.get(raw_cls, "").lower()

            if "pothole" in raw_name or raw_cls == 3:
                cls_id = 3
            elif "alligator" in raw_name or raw_cls == 2:
                cls_id = 2
            elif "transverse" in raw_name or raw_cls == 1:
                cls_id = 1
            else:
                cls_id = 0

            coords = b.xyxy[0].tolist()
            xmin = max(0.0, min(float(img_w), float(coords[0])))
            ymin = max(0.0, min(float(img_h), float(coords[1])))
            xmax = max(0.0, min(float(img_w), float(coords[2])))
            ymax = max(0.0, min(float(img_h), float(coords[3])))

            corr_dets.append({
                "class_id": cls_id,
                "class_name": ROADGUARD_TAXONOMY[cls_id],
                "confidence": conf,
                "bbox": {"xmin": round(xmin, 2), "ymin": round(ymin, 2), "xmax": round(xmax, 2), "ymax": round(ymax, 2)}
            })
            class_stats_corr[cls_id] += 1

        # Save Visualizations
        draw_boxes(img_path, orig_dets, Path("ml/evaluation/investigation_results/original") / f"pred_{img_path.name}", "Original Model (COCO Adapted)")
        draw_boxes(img_path, corr_dets, Path("ml/evaluation/investigation_results/corrected") / f"pred_{img_path.name}", "Corrected Model (RDD2022 Fine-Tuned)")

        item_result = {
            "image": img_path.name,
            "dimensions": f"{img_w}x{img_h}",
            "ground_truth": gt_annotations,
            "original_model_predictions": orig_dets,
            "corrected_model_predictions": corr_dets
        }
        full_report["results"].append(item_result)

        print(f"Image: {img_path.name:<18} | GT Instances: {len(gt_annotations)} | Orig Dets: {len(orig_dets)} | Corr Dets: {len(corr_dets)}")
        if gt_annotations:
            gt_classes = [g['class_name'].split('_')[0] for g in gt_annotations]
            corr_classes = [c['class_name'].split('_')[0] for c in corr_dets]
            orig_classes = [o['class_name'].split('_')[0] for o in orig_dets]
            print(f"  GT: {gt_classes} -> Orig: {orig_classes} | Corrected: {corr_classes}")

    # Write summary log
    report_json_path = Path("ml/evaluation/investigation_results/investigation_summary.json")
    with open(report_json_path, "w") as f:
        json.dump(full_report, f, indent=2)

    print("\n" + "=" * 70)
    print(" INVESTIGATION SUMMARY & CLASS DISTRIBUTION COMPARISON")
    print("=" * 70)
    print(f"Ground Truth Total Annotations: {gt_total_counts}")
    print(f"Original Model Class Distribution: {class_stats_orig}")
    print(f"Corrected Model Class Distribution: {class_stats_corr}")
    print(f"\nDetailed JSON audit report saved to: {report_json_path}")


if __name__ == "__main__":
    run_investigation()

