"""
RoadGuard - Pascal VOC XML to YOLO TXT Annotation Converter
Converts RDD2022 Pascal VOC XML bounding box annotations to normalized YOLO format.
Supported Damage Classes:
  0: D00 - Longitudinal Crack
  1: D10 - Transverse Crack
  2: D20 - Alligator Crack
  3: D40 - Pothole
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Tuple, List

# RDD2022 Standard Class Mapping
CLASS_MAPPING: Dict[str, int] = {
    "D00": 0,  # Longitudinal crack
    "D10": 1,  # Transverse crack
    "D20": 2,  # Alligator crack
    "D40": 3,  # Pothole
}

CLASS_NAMES: Dict[int, str] = {
    0: "D00_Longitudinal_Crack",
    1: "D10_Transverse_Crack",
    2: "D20_Alligator_Crack",
    3: "D40_Pothole",
}


def convert_voc_bbox(size: Tuple[int, int], box: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """Convert Pascal VOC bounding box (xmin, ymin, xmax, ymax) to YOLO normalized (x_center, y_center, width, height)."""
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    
    xmin, ymin, xmax, ymax = box
    
    # Clip coordinates to image boundary
    xmin = max(0.0, min(float(xmin), float(size[0])))
    xmax = max(0.0, min(float(xmax), float(size[0])))
    ymin = max(0.0, min(float(ymin), float(size[1])))
    ymax = max(0.0, min(float(ymax), float(size[1])))
    
    x_center = ((xmin + xmax) / 2.0) * dw
    y_center = ((ymin + ymax) / 2.0) * dh
    width = (xmax - xmin) * dw
    height = (ymax - ymin) * dh
    
    return (round(x_center, 6), round(y_center, 6), round(width, 6), round(height, 6))


def convert_xml_file(xml_path: Path, output_txt_path: Path) -> List[int]:
    """Parse one XML annotation file and write corresponding YOLO format TXT file."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML {xml_path}: {e}")
        return []

    size_elem = root.find("size")
    if size_elem is None:
        return []

    width = int(size_elem.find("width").text)
    height = int(size_elem.find("height").text)

    if width <= 0 or height <= 0:
        return []

    lines = []
    classes_found = []

    for obj in root.findall("object"):
        name_elem = obj.find("name")
        if name_elem is None:
            continue
        cls_name = name_elem.text.strip()
        
        # Match class code
        matched_class = None
        for key in CLASS_MAPPING:
            if cls_name == key or cls_name.startswith(key):
                matched_class = CLASS_MAPPING[key]
                break

        if matched_class is None:
            continue  # Ignore auxiliary non-damage tags if any

        bndbox = obj.find("bndbox")
        if bndbox is None:
            continue

        xmin = float(bndbox.find("xmin").text)
        ymin = float(bndbox.find("ymin").text)
        xmax = float(bndbox.find("xmax").text)
        ymax = float(bndbox.find("ymax").text)

        if xmax <= xmin or ymax <= ymin:
            continue

        yolo_box = convert_voc_bbox((width, height), (xmin, ymin, xmax, ymax))
        lines.append(f"{matched_class} {yolo_box[0]} {yolo_box[1]} {yolo_box[2]} {yolo_box[3]}")
        classes_found.append(matched_class)

    output_txt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return classes_found


def convert_directory(xml_dir: Path, output_labels_dir: Path):
    """Convert all XML files in a directory to YOLO txt files."""
    xml_files = list(xml_dir.glob("*.xml"))
    print(f"Found {len(xml_files)} XML annotations in {xml_dir}")
    
    stats = {0: 0, 1: 0, 2: 0, 3: 0}
    converted_count = 0

    for xml_path in xml_files:
        txt_name = xml_path.stem + ".txt"
        out_txt = output_labels_dir / txt_name
        classes = convert_xml_file(xml_path, out_txt)
        if classes:
            converted_count += 1
            for c in classes:
                stats[c] = stats.get(c, 0) + 1

    print(f"\nSuccessfully converted {converted_count} files.")
    print("Class Instance Statistics:")
    for cls_id, count in stats.items():
        print(f"  Class {cls_id} ({CLASS_NAMES[cls_id]}): {count} instances")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert RDD2022 VOC XML to YOLO format")
    parser.add_argument("--xml_dir", type=str, required=True, help="Directory containing .xml files")
    parser.add_argument("--labels_dir", type=str, required=True, help="Directory to save .txt YOLO labels")
    args = parser.parse_args()

    convert_directory(Path(args.xml_dir).resolve(), Path(args.labels_dir).resolve())

