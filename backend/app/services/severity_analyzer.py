"""
RoadGuard - Road Damage Severity Index (RDSI) Engine
Implements mathematically formal, physically calibrated severity estimation modeled after ASTM D6433 & PCI deduct methodologies.
"""

import math
from typing import List, Dict, Any, Tuple

# Hazard weights representing structural damage threat
CLASS_HAZARD_WEIGHTS = {
    "D00": 1.0,  # Longitudinal Crack
    "D10": 1.2,  # Transverse Crack
    "D20": 2.2,  # Alligator Crack (Structural Fatigue)
    "D40": 3.0,  # Pothole (Cavitation & Safety Hazard)
}

DEFAULT_WEIGHT = 1.0


# Experimental assessment disclaimer for engineering integrity
EXPERIMENTATION_DISCLAIMER = (
    "EXPERIMENTAL ESTIMATE (Non-Certified): Severity levels and Road Damage Severity Index (RDSI) "
    "scores are heuristic screening estimates derived solely from 2D bounding-box spatial coverage "
    "and model detection confidence. They do NOT constitute a certified civil engineering pavement rating "
    "(such as ASTM D6433 Pavement Condition Index core extraction). On-site depth measurement and "
    "geotechnical engineer sign-off are required prior to structural remediation."
)


class SeverityAnalyzer:
    DISCLAIMER = EXPERIMENTATION_DISCLAIMER

    @staticmethod
    def get_class_weight(class_name: str) -> float:
        # Extract class code prefix (D00, D10, D20, D40)
        for code, weight in CLASS_HAZARD_WEIGHTS.items():
            if code in class_name.upper():
                return weight
        return DEFAULT_WEIGHT

    @staticmethod
    def calculate_instance_severity(
        bbox: Dict[str, float],
        confidence: float,
        class_name: str,
        image_width: int,
        image_height: int
    ) -> Tuple[float, float, str]:
        """
        Calculates area ratio, instance severity score (0-100), and severity tag for a single damage instance.
        """
        box_w = max(0.0, bbox["xmax"] - bbox["xmin"])
        box_h = max(0.0, bbox["ymax"] - bbox["ymin"])
        box_area = box_w * box_h
        total_img_area = max(1.0, float(image_width * image_height))
        
        area_ratio = box_area / total_img_area
        w_c = SeverityAnalyzer.get_class_weight(class_name)
        
        # Instance severity formula: s_i = w_c * (sqrt(alpha_i) * 100) * (0.5 + 0.5 * conf)
        # Using square root normalizes thin linear cracks against planar potholes
        raw_score = w_c * (math.sqrt(area_ratio) * 100.0) * (0.5 + 0.5 * confidence)
        instance_score = round(min(100.0, max(0.0, raw_score)), 2)

        if instance_score < 25.0:
            tag = "Low"
        elif instance_score < 60.0:
            tag = "Medium"
        else:
            tag = "High"

        return round(area_ratio, 6), instance_score, tag

    @staticmethod
    def calculate_frame_severity(instances: List[Dict[str, Any]]) -> Tuple[float, str]:
        """
        Computes cumulative Road Damage Severity Index (RDSI) across all instances in a frame.
        Formula: RDSI = min(100, 0.6 * max(s_i) + 0.4 * sum(s_i) / sqrt(N))
        """
        if not instances:
            return 0.0, "Low"

        scores = [inst["instance_severity"] for inst in instances]
        max_score = max(scores)
        sum_scores = sum(scores)
        n = len(instances)

        # Damp aggregate multi-crack inflation using sub-linear factor
        aggregate_component = sum_scores / math.sqrt(n)

        # Compounding multi-pothole hazard factor:
        # A single small pothole is low priority, but multiple co-occurring potholes represent
        # hazardous lane cavitation that damages wheel assemblies and creates collision avoidance risks
        pothole_count = sum(
            1 for inst in instances
            if "D40" in str(inst.get("class_name", "")).upper() or inst.get("class_id") == 3
        )
        density_multiplier = 1.0
        if pothole_count >= 3:
            density_multiplier = 1.50
        elif pothole_count == 2:
            density_multiplier = 1.30

        raw_cumulative = (0.6 * max_score + 0.4 * aggregate_component) * density_multiplier
        cumulative_rdsi = round(min(100.0, max(0.0, raw_cumulative)), 2)

        if cumulative_rdsi < 25.0:
            overall_level = "Low"
        elif cumulative_rdsi < 60.0:
            overall_level = "Medium"
        else:
            overall_level = "High"

        return cumulative_rdsi, overall_level

