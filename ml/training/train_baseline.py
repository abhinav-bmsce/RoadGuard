"""
RoadGuard - Baseline YOLOv8 Model Training Script
Trains a lightweight YOLOv8n model on the RDD2022 road damage dataset.
"""

import os
import argparse
from pathlib import Path
from ultralytics import YOLO


def train_baseline(
    data_yaml: str,
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 32,
    device: str = "0",
    project: str = "runs/train",
    name: str = "roadguard_yolov8n_baseline"
):
    print("=" * 60)
    print(" RoadGuard - YOLOv8n Baseline Training on RDD2022")
    print("=" * 60)
    print(f"Data YAML: {data_yaml}")
    print(f"Epochs: {epochs} | Batch: {batch} | Img Size: {imgsz} | Device: {device}")

    # Load baseline lightweight pretrained model
    model = YOLO("yolov8n.pt")

    # Train the model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=project,
        name=name,
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        weight_decay=0.0005,
        patience=15,
        save=True,
        save_period=10,
        val=True,
        plots=True,
        verbose=True
    )

    print("\nTraining complete!")
    print(f"Best model weights saved at: {Path(project) / name / 'weights' / 'best.pt'}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Baseline YOLOv8 on RDD2022")
    parser.add_argument("--data", type=str, default="ml/dataset/rdd2022.yaml", help="Path to data YAML")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=32, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image size")
    parser.add_argument("--device", type=str, default="0", help="GPU device ID or 'cpu' or 'mps'")
    args = parser.parse_args()

    train_baseline(
        data_yaml=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device
    )

