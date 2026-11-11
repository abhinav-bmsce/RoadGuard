"""
RoadGuard - Model Exporter
Exports PyTorch YOLOv8 weights to ONNX format for accelerated cross-platform deployment.
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def export_model(weights_path: str, format: str = "onnx", imgsz: int = 640):
    print(f"Loading weights from {weights_path}...")
    model = YOLO(weights_path)
    print(f"Exporting to {format.upper()} (imgsz={imgsz})...")
    exported_path = model.export(format=format, imgsz=imgsz, dynamic=True, simplify=True)
    print(f"Successfully exported model to: {exported_path}")
    return exported_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export RoadGuard Model to ONNX")
    parser.add_argument("--weights", type=str, default="ml/models/roadguard_yolov8n.pt")
    parser.add_argument("--format", type=str, default="onnx")
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    export_model(args.weights, args.format, args.imgsz)

