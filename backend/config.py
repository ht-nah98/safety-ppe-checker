"""
Safety PPE Checker — Application Configuration

Centralized settings for thresholds, paths, class mapping.
Referenced by: cv_engine.py, main.py, routers
Guardrail: .agent/skills/ppe_project_guardrails/SKILL.md
"""

import os
from pathlib import Path

# =============================================================
# PATHS
# =============================================================
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
RESULTS_DIR = STATIC_DIR / "results"
ORIGINALS_DIR = STATIC_DIR / "originals"
MODELS_DIR = BASE_DIR / "models_weights"
DATA_DIR = BASE_DIR.parent / "data"

# Ensure directories exist at import time
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================
# DATABASE
# =============================================================
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'ppe_checker.db'}")

# =============================================================
# MODEL
# =============================================================
MODEL_PATH = os.getenv("MODEL_PATH", str(MODELS_DIR / "best.pt"))

# Fallback: try yolov8n.pt (pretrained) if custom model not found
MODEL_FALLBACK_PATH = str(MODELS_DIR / "yolov8n.pt")

# =============================================================
# PPE CLASS MAPPING — MISSION CRITICAL
# Maps dataset class names → project standard class names
# Source: DATA-STRATEGY.md Section 5
# =============================================================
PPE_CLASS_MAP = {
    # Construction-PPE dataset (Ultralytics) — PRIMARY
    "helmet":   "helmet",
    "vest":     "reflective_vest",
    "gloves":   "gloves",
    "boots":    "safety_boots",
    "goggles":  "safety_glasses",
    # SH17 dataset — SUPPLEMENT
    "Helmet":        "helmet",
    "Safety-vest":   "reflective_vest",
    "Gloves":        "gloves",
    "Shoes":         "safety_boots",
    "Glasses":       "safety_glasses",
}

# The 5 required PPE classes (in display order)
REQUIRED_PPE_CLASSES = [
    "helmet",
    "reflective_vest",
    "gloves",
    "safety_boots",
    "safety_glasses",
]

# =============================================================
# CONFIDENCE THRESHOLDS
# Guardrail: helmet/vest = 0.50, gloves/glasses/boots = 0.40
# =============================================================
CONFIDENCE_THRESHOLDS = {
    "helmet":          0.50,
    "reflective_vest": 0.50,
    "gloves":          0.40,
    "safety_boots":    0.45,
    "safety_glasses":  0.40,
}

# Global minimum confidence for YOLO inference (pre-filter)
INFERENCE_CONF = 0.25

# =============================================================
# FILE UPLOAD LIMITS
# =============================================================
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_DIMENSION = 1280  # Resize longest side to this

# =============================================================
# ANNOTATION VISUALS
# =============================================================
BBOX_COLOR_DETECTED = (0, 200, 81)     # Green in BGR
BBOX_COLOR_MISSING = (68, 68, 239)     # Red in BGR
BBOX_THICKNESS = 2
FONT_SCALE = 0.6

# =============================================================
# CORS — Frontend origins allowed
# =============================================================
CORS_ORIGINS = [
    "http://localhost:3000",     # Docker frontend
    "http://localhost:5173",     # Vite dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# =============================================================
# PPE DISPLAY LABELS (Vietnamese)
# =============================================================
PPE_LABELS = {
    "helmet":          "Mũ bảo hộ",
    "reflective_vest": "Áo phản quang",
    "gloves":          "Găng tay bảo hộ",
    "safety_boots":    "Giày bảo hộ",
    "safety_glasses":  "Kính bảo hộ",
}
