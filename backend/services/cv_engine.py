"""
CV Engine — Core AI Detection Service

Responsibilities:
1. Load YOLOv8 model (singleton, once at startup)
2. Run inference on uploaded images
3. Map detections → 5 PPE classes using PPE_CLASS_MAP
4. Determine overall PASS/FAIL
5. Annotate image with bounding boxes
6. Return structured result

Guardrail: config.py is the SINGLE source of truth for class mapping & thresholds.
Reference: TP-CV-001, DATA-STRATEGY.md
"""

import time
import logging
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from config import (
    PPE_CLASS_MAP,
    REQUIRED_PPE_CLASSES,
    CONFIDENCE_THRESHOLDS,
    INFERENCE_CONF,
    MAX_IMAGE_DIMENSION,
    RESULTS_DIR,
    ORIGINALS_DIR,
    BBOX_COLOR_DETECTED,
    BBOX_THICKNESS,
    FONT_SCALE,
    MODEL_PATH,
    MODEL_FALLBACK_PATH,
)

logger = logging.getLogger(__name__)


class CVEngine:
    """
    Singleton-style CV Engine.
    Load model once, reuse for all requests.
    """

    def __init__(self, model_path: str = None):
        """
        Initialize the YOLO model.
        Tries custom model first, falls back to pretrained yolov8n.
        """
        path = model_path or MODEL_PATH
        if not Path(path).exists():
            logger.warning(
                f"Custom model not found at {path}. "
                f"Trying fallback: {MODEL_FALLBACK_PATH}"
            )
            path = MODEL_FALLBACK_PATH

        if not Path(path).exists():
            logger.warning(
                f"Fallback model not found. Will download yolov8n.pt on first use."
            )
            path = "yolov8n.pt"  # Ultralytics will auto-download

        logger.info(f"Loading YOLO model from: {path}")
        self.model = YOLO(path)
        self._warmup()
        logger.info("CV Engine ready ✅")

    def _warmup(self):
        """Run dummy inference to warm up model (loads weights into memory)."""
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self.model.predict(dummy, verbose=False)
        logger.info("Model warmup complete")

    def run(self, image_bytes: bytes, inspection_id: str) -> dict:
        """
        Main inference pipeline.

        Args:
            image_bytes: Raw bytes of uploaded image
            inspection_id: UUID for this inspection

        Returns:
            dict with keys: items, overall_pass, annotated_image_path,
                           original_image_path, processing_time_ms
        """
        t_start = time.time()

        # 1. Decode image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image. File may be corrupted.")

        # 2. Save original
        original_path = str(ORIGINALS_DIR / f"{inspection_id}.jpg")
        cv2.imwrite(original_path, img, [cv2.IMWRITE_JPEG_QUALITY, 90])

        # 3. Resize for inference (keep aspect ratio)
        img_resized = self._resize(img, MAX_IMAGE_DIMENSION)

        # 4. Run YOLOv8 inference
        results = self.model.predict(
            img_resized,
            conf=INFERENCE_CONF,
            verbose=False,
        )[0]

        # 5. Map detections → PPE checklist
        items = {
            cls: {"detected": False, "confidence": 0.0}
            for cls in REQUIRED_PPE_CLASSES
        }
        boxes_to_draw = []

        raw_detections = []  # All detections before threshold filter
        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = self.model.names[cls_id]
            conf = float(box.conf[0])

            ppe_class = PPE_CLASS_MAP.get(cls_name)
            threshold = CONFIDENCE_THRESHOLDS.get(ppe_class, 0.50) if ppe_class else None

            raw_detections.append({
                "raw_class": cls_name,
                "ppe_class": ppe_class,
                "confidence": round(conf, 3),
                "threshold": threshold,
                "passed_threshold": (ppe_class is not None and conf >= threshold),
            })

            # Map dataset class → project class
            if ppe_class is None:
                continue  # Skip classes we don't care about (e.g., "Person")

            # Check against per-class threshold
            if conf >= threshold:
                # Keep the detection with highest confidence
                if not items[ppe_class]["detected"] or conf > items[ppe_class]["confidence"]:
                    items[ppe_class] = {
                        "detected": True,
                        "confidence": round(conf, 2),
                    }
                    coords = box.xyxy[0].tolist()
                    boxes_to_draw.append((coords, ppe_class, conf))

        # 6. Determine overall pass (ALL 5 must be detected)
        overall_pass = all(v["detected"] for v in items.values())

        # 7. Annotate image
        annotated_path = self._annotate(img_resized, boxes_to_draw, inspection_id)

        # 8. Calculate processing time
        processing_ms = int((time.time() - t_start) * 1000)

        logger.info(
            f"Inspection {inspection_id[:8]}: "
            f"{'PASS' if overall_pass else 'FAIL'} "
            f"({processing_ms}ms) "
            f"Raw detections: {len(raw_detections)} | "
            f"Detected PPE: {[k for k, v in items.items() if v['detected']]}"
        )

        return {
            "items": items,
            "overall_pass": overall_pass,
            "annotated_image_path": f"static/results/{inspection_id}_annotated.jpg",
            "original_image_path": original_path,
            "processing_time_ms": processing_ms,
            "debug_info": {
                "model_path": str(self.model.model_name if hasattr(self.model, 'model_name') else "unknown"),
                "inference_conf_threshold": INFERENCE_CONF,
                "raw_detection_count": len(raw_detections),
                "raw_detections": raw_detections,
                "image_size": list(img_resized.shape[:2]),
            },
        }

    def _resize(self, img: np.ndarray, max_size: int) -> np.ndarray:
        """Resize image keeping aspect ratio. Only downscale."""
        h, w = img.shape[:2]
        if max(h, w) <= max_size:
            return img
        scale = max_size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def _annotate(
        self,
        img: np.ndarray,
        boxes: list,
        inspection_id: str,
    ) -> str:
        """
        Draw bounding boxes and labels on image.
        Returns path to saved annotated image.
        """
        annotated = img.copy()

        for (x1, y1, x2, y2), ppe_class, conf in boxes:
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Draw bounding box
            cv2.rectangle(
                annotated, (x1, y1), (x2, y2),
                BBOX_COLOR_DETECTED, BBOX_THICKNESS,
            )

            # Draw label background
            label = f"{ppe_class} {conf:.0%}"
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, 1
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - label_h - baseline - 5),
                (x1 + label_w + 5, y1),
                BBOX_COLOR_DETECTED,
                cv2.FILLED,
            )

            # Draw label text (white on green background)
            cv2.putText(
                annotated, label,
                (x1 + 2, y1 - baseline - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                FONT_SCALE,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        # Save
        out_path = str(RESULTS_DIR / f"{inspection_id}_annotated.jpg")
        cv2.imwrite(out_path, annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])

        return out_path
