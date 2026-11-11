"""
RoadGuard - Stratified Dataset Splitter
Partitions images and YOLO labels into train (70%), val (15%), and test (15%) splits.
"""

import os
import shutil
import random
from pathlib import Path
import argparse


def split_data(images_dir: Path, labels_dir: Path, output_dir: Path, train_ratio=0.70, val_ratio=0.15, seed=42):
    random.seed(seed)
    
    image_extensions = {".jpg", ".jpeg", ".png"}
    all_images = [p for p in images_dir.iterdir() if p.suffix.lower() in image_extensions]
    
    print(f"Total images found: {len(all_images)}")
    if len(all_images) == 0:
        print("No images found in images_dir!")
        return

    # Check for corresponding labels
    valid_pairs = []
    for img_path in all_images:
        label_path = labels_dir / f"{img_path.stem}.txt"
        if label_path.exists():
            valid_pairs.append((img_path, label_path))

    print(f"Matched image-label pairs: {len(valid_pairs)}")
    random.shuffle(valid_pairs)

    n_total = len(valid_pairs)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    splits = {
        "train": valid_pairs[:n_train],
        "val": valid_pairs[n_train:n_train + n_val],
        "test": valid_pairs[n_train + n_val:]
    }

    for split_name, pairs in splits.items():
        split_img_dir = output_dir / "images" / split_name
        split_lbl_dir = output_dir / "labels" / split_name
        split_img_dir.mkdir(parents=True, exist_ok=True)
        split_lbl_dir.mkdir(parents=True, exist_ok=True)

        for img_p, lbl_p in pairs:
            shutil.copy2(img_p, split_img_dir / img_p.name)
            shutil.copy2(lbl_p, split_lbl_dir / lbl_p.name)

        print(f"Split '{split_name}': {len(pairs)} samples saved to {split_img_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split dataset into train, val, and test subsets")
    parser.add_argument("--images", type=str, required=True, help="Directory containing raw images")
    parser.add_argument("--labels", type=str, required=True, help="Directory containing YOLO labels")
    parser.add_argument("--output", type=str, default="./ml/dataset/processed", help="Output dataset root")
    args = parser.parse_args()

    split_data(Path(args.images), Path(args.labels), Path(args.output))

