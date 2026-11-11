"""
RoadGuard - Deep Learning Inference Engine
Manages YOLOv8 PyTorch model lifecycle, hardware acceleration (CPU / Apple Silicon MPS / CUDA),
real forward-pass inference, and bounding box decoding.
"""

import time
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import cv2
import torch
from ultralytics import YOLO

from backend.app.core.config import settings
from backend.app.core.logging import logger

# Canonical RoadGuard RDD2022 class map
ROADGUARD_CLASSES = {
    0: "D00_Longitudinal_Crack",
    1: "D10_Transverse_Crack",
    2: "D20_Alligator_Crack",
    3: "D40_Pothole",
}


class InferenceEngine:
    _instance = None
    _model = None
    _device = "cpu"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InferenceEngine, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        # Configure YOLO directory
        os.environ["YOLO_CONFIG_DIR"] = settings.YOLO_CONFIG_DIR

        # Select hardware device
        req_dev = settings.MODEL_DEVICE.lower()
        if req_dev == "mps" and torch.backends.mps.is_available():
            self._device = "mps"
        elif req_dev == "cuda" and torch.cuda.is_available():
            self._device = "cuda"
        else:
            self._device = "cpu"

        # Resolve model path reliably against project root if relative
        raw_path = Path(settings.MODEL_PATH)
        if raw_path.is_absolute():
            model_path = raw_path
        else:
            base_dir = getattr(settings, "BASE_DIR", Path.cwd())
            model_path = (Path(base_dir) / raw_path).resolve()

        if not model_path.exists():
            error_msg = (
                f"Trained YOLO model weights not found at: '{model_path}'. "
                f"Please ensure 'best.pt' is present at the configured path."
            )
            logger.critical(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading RoadGuard YOLO model from {model_path} onto {self._device}...")
        try:
            self._model = YOLO(str(model_path))
            logger.info(f"Model loaded successfully with {len(self._model.names)} output classes: {self._model.names}")
        except Exception as e:
            error_msg = f"Failed to initialize YOLO model from '{model_path}': {str(e)}"
            logger.critical(error_msg)
            raise RuntimeError(error_msg) from e

        # Warm up graph compilation and memory allocators to eliminate cold-start latency (~800ms)
        try:
            import numpy as np
            dummy_img = np.zeros((448, 448, 3), dtype=np.uint8)
            _ = self._model.predict(source=dummy_img, imgsz=448, device=self._device, verbose=False)
            logger.info("Inference engine warm-up completed: graph initialized for sub-50ms inference.")
        except Exception as e:
            logger.warning(f"Inference engine warm-up notice: {e}")

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def device_name(self) -> str:
        return self._device

    def detect(
        self,
        image_path: str,
        conf_threshold: float = None,
        iou_threshold: float = None
    ) -> Tuple[List[Dict[str, Any]], float, int, int]:
        """
        Executes actual deep learning forward pass.
        Returns:
            - list of detected damage dictionaries
            - pure inference latency in ms
            - original image width
            - original image height
        """
        if self._model is None:
            self._initialize_model()

        conf = conf_threshold if conf_threshold is not None else settings.MODEL_CONFIDENCE_THRESHOLD
        iou = iou_threshold if iou_threshold is not None else settings.MODEL_IOU_THRESHOLD

        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        img_h, img_w = img.shape[:2]

        # Compute native-aware resolution (clamped to multiple of 32 between 384 and 1280)
        # Prevents interpolation blurring on small/compressed images and preserves fine distress features
        target_sz = max(384, min(1280, int(round(max(img_w, img_h) / 32.0) * 32)))

        t0 = time.perf_counter()
        results = self._model.predict(
            source=img,
            imgsz=target_sz,
            augment=True,
            conf=conf,
            iou=iou,
            device=self._device,
            verbose=False
        )

        # Multi-scale pyramid fallback: if 0 detections at native scale and target_sz != 640,
        # perform an auxiliary pass at canonical 640 scale to handle scale-invariant anomalies
        if len(results[0].boxes) == 0 and target_sz != 640:
            results_aux = self._model.predict(
                source=img,
                imgsz=640,
                augment=True,
                conf=conf,
                iou=iou,
                device=self._device,
                verbose=False
            )
            if len(results_aux[0].boxes) > 0:
                results = results_aux

        t1 = time.perf_counter()
        inference_time_ms = round((t1 - t0) * 1000.0, 2)

        raw_result = results[0]
        boxes = raw_result.boxes

        damages: List[Dict[str, Any]] = []

        for box in boxes:
            raw_cls_id = int(box.cls[0].item())
            conf_val = round(float(box.conf[0].item()), 4)

            # Map class ID and label name to canonical RoadGuard RDD2022 taxonomy
            raw_name = self._model.names.get(raw_cls_id, "").lower() if self._model else ""
            
            if "pothole" in raw_name or raw_cls_id == 3:
                cls_id = 3
                cls_name = "D40_Pothole"
            elif "alligator" in raw_name or raw_cls_id == 2:
                cls_id = 2
                cls_name = "D20_Alligator_Crack"
            elif "transverse" in raw_name or raw_cls_id == 1:
                cls_id = 1
                cls_name = "D10_Transverse_Crack"
            elif "longitudinal" in raw_name or raw_cls_id == 0:
                cls_id = 0
                cls_name = "D00_Longitudinal_Crack"
            elif raw_cls_id in ROADGUARD_CLASSES:
                cls_id = raw_cls_id
                cls_name = ROADGUARD_CLASSES[raw_cls_id]
            else:
                logger.warning(f"Unrecognized class index {raw_cls_id} ({raw_name}) - skipping out-of-domain detection.")
                continue

            coords = box.xyxy[0].tolist()
            # Explicit coordinate clipping to image canvas dimensions
            xmin = max(0.0, min(float(img_w), float(coords[0])))
            ymin = max(0.0, min(float(img_h), float(coords[1])))
            xmax = max(0.0, min(float(img_w), float(coords[2])))
            ymax = max(0.0, min(float(img_h), float(coords[3])))

            # Discard degenerated or inverted boxes
            if xmax <= xmin or ymax <= ymin:
                continue

            bbox = {
                "xmin": round(xmin, 2),
                "ymin": round(ymin, 2),
                "xmax": round(xmax, 2),
                "ymax": round(ymax, 2),
            }

            damages.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": conf_val,
                "bbox": bbox,
            })

        logger.info(f"Inference completed in {inference_time_ms} ms: {len(damages)} damages detected.")
        return damages, inference_time_ms, img_w, img_h


inference_engine = InferenceEngine()

