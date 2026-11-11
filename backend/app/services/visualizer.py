"""
RoadGuard - Road Damage Visualizer
Draws high-visibility bounding boxes and diagnostic status labels over road damage detections.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# BGR Color scheme
COLOR_MAP = {
    "Low": (129, 185, 16),     # Emerald Green
    "Medium": (11, 158, 245),  # Amber Orange
    "High": (68, 68, 239),     # Crimson Red
}


class Visualizer:
    @staticmethod
    def annotate_image(
        image_path: str,
        damages: List[Dict[str, Any]],
        output_path: str,
        overall_severity: str = "Low",
        overall_score: float = 0.0
    ) -> str:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Unable to read image from {image_path}")

        h, w, _ = img.shape

        # Draw each detected damage instance
        for item in damages:
            bbox = item["bbox"]
            cls_name = item["class_name"]
            conf = item["confidence"]
            tag = item.get("severity_tag", "Low")
            color = COLOR_MAP.get(tag, (129, 185, 16))

            x1 = int(max(0, min(w, bbox["xmin"])))
            y1 = int(max(0, min(h, bbox["ymin"])))
            x2 = int(max(0, min(w, bbox["xmax"])))
            y2 = int(max(0, min(h, bbox["ymax"])))

            # Draw outer rectangle
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness=3)

            # Label text
            short_class = cls_name.split("_")[0] if "_" in cls_name else cls_name
            label = f"{short_class} | {conf*100:.0f}% | {tag}"

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.55
            thickness = 2
            (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)

            # Background rectangle for text
            label_y1 = max(0, y1 - text_h - 10)
            label_y2 = y1
            label_x2 = min(w, x1 + text_w + 10)

            # Draw label background
            cv2.rectangle(img, (x1, label_y1), (label_x2, label_y2), color, -1)
            # Draw white text
            cv2.putText(
                img,
                label,
                (x1 + 5, y1 - 5),
                font,
                font_scale,
                (255, 255, 255),
                thickness=thickness,
                lineType=cv2.LINE_AA
            )

        # Draw top banner with RoadGuard watermark and overall severity rating
        banner_h = 42
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, banner_h), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)

        header_text = f"RoadGuard AI  |  Damages: {len(damages)}  |  Severity: {overall_severity} (RDSI: {overall_score:.1f})"
        status_color = COLOR_MAP.get(overall_severity, (255, 255, 255))
        cv2.putText(img, header_text, (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (241, 245, 249), 2, cv2.LINE_AA)
        # Small colored status indicator dot
        cv2.circle(img, (w - 30, 21), 9, status_color, -1)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, img)
        return output_path

