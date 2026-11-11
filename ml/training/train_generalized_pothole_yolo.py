"""
RoadGuard - Cross-Domain Generalized YOLOv8 Training Script
Optimized for Google Colab GPU / High Performance Workstation

Fine-tunes YOLOv8 on combined RDD2022 + Multi-Domain Pothole Datasets
with specialized cross-domain augmentations to prevent pothole missed detections
and eliminate crack misclassifications.
"""

import os
import argparse
from pathlib import Path
from ultralytics import YOLO


def train_generalized_model(
    data_yaml: str,
    base_model: str = "yolov8s.pt",
    epochs: int = 50,
    batch_size: int = 16,
    imgsz: int = 640,
    device: str = "0",
    output_dir: str = "runs/roadguard_generalized"
):
    print("=" * 60)
    print("RoadGuard: Starting Cross-Domain Generalized Training")
    print(f"Data configuration: {data_yaml}")
    print(f"Base architecture: {base_model}")
    print(f"Epochs: {epochs}, Batch size: {batch_size}, Image size: {imgsz}")
    print("=" * 60)

    model = YOLO(base_model)

    # Domain Adaptation Augmentations:
    # 1. hsv_s / hsv_v: Robustness to underexposed, dusk, harsh sunlight, wet pavement
    # 2. scale=0.5: Robustness to distant small potholes and close-up cavities
    # 3. degrees=10.0: Robustness to handheld, oblique, and unaligned camera perspectives
    # 4. mosaic=1.0 + mixup=0.15: Robustness to dense co-occurring cracks and road cavities
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=device,
        project=output_dir,
        name="roadguard_generalized_yolov8",
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        # Augmentation hyperparameters
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.0005,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.15,
        copy_paste=0.1,
        # Early stopping and saving
        patience=12,
        save=True,
        save_period=5,
        verbose=True
    )

    print("Training complete!")
    print(f"Best model weights saved at: {output_dir}/roadguard_generalized_yolov8/weights/best.pt")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RoadGuard Generalized YOLOv8")
    parser.add_argument("--data", type=str, default="data/roadguard_combined/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", type=str, default="yolov8s.pt", help="Base model weights (yolov8n.pt or yolov8s.pt)")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Input resolution")
    parser.add_argument("--device", type=str, default="0", help="CUDA device index or 'mps'/'cpu'")
    parser.add_argument("--project", type=str, default="runs/roadguard_generalized", help="Output directory")

    args = parser.parse_args()
    train_generalized_model(
        data_yaml=args.data,
        base_model=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        output_dir=args.project
    )

