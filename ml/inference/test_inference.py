"""
RoadGuard - Standalone Model Inference Script
Verifies model inference pipeline on a given input image, calculates detection bounding boxes, and prints category details.
"""

import sys
import argparse
from pathlib import Path
from ultralytics import YOLO
import cv2


def run_inference(image_path: str, model_path: str = "ml/models/roadguard_yolov8n.pt", conf_thresh: float = 0.25):
    print("=" * 60)
    print(" RoadGuard - Deep Learning Inference Verification")
    print(f"Image: {image_path}")
    print(f"Model: {model_path}")
    print(f"Confidence Threshold: {conf_thresh}")
    print("=" * 60)

    model = YOLO(model_path)
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image at {image_path}")
        return

    results = model.predict(source=img, conf=conf_thresh, verbose=False)
    result = results[0]

    boxes = result.boxes
    print(f"\nTotal detections found: {len(boxes)}")
    for i, box in enumerate(boxes):
        cls_id = int(box.cls[0].item())
        cls_name = model.names.get(cls_id, f"Class_{cls_id}")
        conf = float(box.conf[0].item())
        xyxy = [round(float(v), 2) for v in box.xyxy[0].tolist()]
        print(f"  [{i+1}] {cls_name:<25} | Conf: {conf*100:.1f}% | Box: {xyxy}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test RoadGuard Inference")
    parser.add_argument("--image", type=str, default="ml/inference/samples/road_pothole_severe.jpg")
    parser.add_argument("--model", type=str, default="ml/models/roadguard_yolov8n.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    run_inference(args.image, args.model, args.conf)

