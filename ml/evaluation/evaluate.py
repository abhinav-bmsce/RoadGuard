"""
RoadGuard - Model Evaluation Script
Computes precision, recall, mAP@0.5, mAP@0.5:0.95 across road damage categories.
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def evaluate_model(weights_path: str, data_yaml: str, split: str = "val"):
    print("=" * 60)
    print(" RoadGuard - Evaluating Model Benchmark")
    print(f"Weights: {weights_path}")
    print(f"Data YAML: {data_yaml} | Split: {split}")
    print("=" * 60)

    model = YOLO(weights_path)
    metrics = model.val(data=data_yaml, split=split, plots=True)

    print("\n--- Overall Benchmark Results ---")
    print(f"mAP@0.5      : {metrics.box.map50:.4f}")
    print(f"mAP@0.5:0.95 : {metrics.box.map:.4f}")
    print(f"Precision    : {metrics.box.mp:.4f}")
    print(f"Recall       : {metrics.box.mr:.4f}")

    print("\n--- Per-Class Performance ---")
    for idx, (cls_name, ap50, ap) in enumerate(zip(metrics.names.values(), metrics.box.ap50, metrics.box.ap)):
        print(f"  [{idx}] {cls_name:<25}: mAP@0.5 = {ap50:.4f} | mAP@0.5:0.95 = {ap:.4f}")

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RoadGuard YOLO Model")
    parser.add_argument("--weights", type=str, required=True, help="Path to .pt weights")
    parser.add_argument("--data", type=str, default="ml/dataset/rdd2022.yaml", help="Path to data YAML")
    parser.add_argument("--split", type=str, default="val", choices=["val", "test"])
    args = parser.parse_args()

    evaluate_model(args.weights, args.data, args.split)

