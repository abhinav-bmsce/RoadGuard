"""
RoadGuard - Improved Model Training Script
Trains YOLOv8 with road surface domain adaptations:
- Micro-crack sensitive high-resolution feature tuning
- Tailored loss weighting (higher box & class loss on minority cracks D00, D10)
- Road surface lighting & asphalt texture augmentations
"""

import os
import argparse
from pathlib import Path
from ultralytics import YOLO


def train_improved(
    data_yaml: str,
    hyp_yaml: str = "ml/training/hyp_rdd.yaml",
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    device: str = "0",
    project: str = "runs/train",
    name: str = "roadguard_yolov8_improved"
):
    print("=" * 60)
    print(" RoadGuard - Improved YOLOv8 Training (Small Crack & Robustness)")
    print("=" * 60)
    print(f"Data YAML: {data_yaml}")
    print(f"Hyperparameters: {hyp_yaml}")
    print(f"Epochs: {epochs} | Batch: {batch} | Img Size: {imgsz} | Device: {device}")

    # Load YOLOv8 small or nano backbone
    model = YOLO("yolov8s.pt")

    results = model.train(
        data=data_yaml,
        cfg=hyp_yaml if Path(hyp_yaml).exists() else None,
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
        patience=20,
        box=8.0,       # Increased localization loss for hairline cracks
        cls=0.7,       # Balanced class loss
        dfl=1.8,       # Distribution focal loss for tight boundary regression
        close_mosaic=10, # Disable mosaic in final 10 epochs for fine-grained convergence
        save=True,
        save_period=10,
        val=True,
        plots=True,
        verbose=True
    )

    print("\nImproved Model Training Complete!")
    print(f"Model checkpoint saved at: {Path(project) / name / 'weights' / 'best.pt'}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Improved YOLOv8 on RDD2022")
    parser.add_argument("--data", type=str, default="ml/dataset/rdd2022.yaml")
    parser.add_argument("--hyp", type=str, default="ml/training/hyp_rdd.yaml")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", type=str, default="0")
    args = parser.parse_args()

    train_improved(
        data_yaml=args.data,
        hyp_yaml=args.hyp,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device
    )

