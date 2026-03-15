# Technical Specification: TP-CV-001
## CV Engine — PPE Detection API

> **Status**: Draft
> **Linked Epic**: [EPIC-CV-001](../../01_product_requirements/cv-engine/EPIC-CV-001.md)
> **Linked Stories**: US-CV-001, US-CV-002, US-CV-003, US-CV-004
> **Source Files**: `backend/services/cv_engine.py`, `backend/routers/check_ppe.py`

---

## 1. Overview

Module CV Engine là lõi AI của hệ thống. Nó nhận một file ảnh toàn thân công nhân, chạy YOLOv8n inference để detect 5 hạng mục PPE, map kết quả về pass/fail checklist, vẽ bounding box annotate lên ảnh, lưu inspection record vào SQLite, và trả về JSON response đầy đủ cho Frontend.

**Toàn bộ pipeline chạy đồng bộ (synchronous)** — phù hợp cho demo, đủ nhanh với YOLOv8n trên CPU.

---

## 2. API Specifications

### 2.1 Check PPE — Kiểm tra trang bị bảo hộ

**Endpoint**: `POST /api/v1/check-ppe`

**Request Headers**:
- `Content-Type`: `multipart/form-data`

**Request Body**:
```
Form field: image (file)
  - Accepted MIME types: image/jpeg, image/png
  - Max size: 10MB
```

**Response 200 OK**:
```json
{
  "inspection_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "overall_pass": false,
  "processing_time_ms": 1240,
  "annotated_image_url": "/static/results/3fa85f64_annotated.jpg",
  "items": {
    "helmet":          { "detected": true,  "confidence": 0.94 },
    "reflective_vest": { "detected": true,  "confidence": 0.89 },
    "gloves":          { "detected": false, "confidence": 0.0  },
    "safety_boots":    { "detected": true,  "confidence": 0.76 },
    "safety_glasses":  { "detected": false, "confidence": 0.0  }
  }
}
```

**Response Errors**:
| Status | Khi nào | Message |
|--------|---------|---------|
| 400 | File không phải JPEG/PNG | `"Invalid file format. Only JPEG and PNG accepted."` |
| 413 | File > 10MB | `"File too large. Maximum size is 10MB."` |
| 422 | Không có field `image` | FastAPI auto validation error |
| 500 | Model lỗi / inference fail | `"Internal inference error. Please try again."` |

**Logic Flow**:

```
1. VALIDATE REQUEST
   ├── Kiểm tra Content-Type = multipart/form-data
   ├── Kiểm tra field "image" tồn tại
   ├── Kiểm tra file size ≤ 10MB (10 * 1024 * 1024 bytes)
   └── Kiểm tra MIME type in [image/jpeg, image/png]
       ├── FAIL → raise HTTPException(400)
       └── PASS → continue

2. PREPROCESS IMAGE
   ├── Read bytes → numpy array (cv2.imdecode)
   ├── Resize nếu cần (max 1280px longest side, keep ratio)
   └── Save original image → static/originals/{uuid}.jpg

3. RUN YOLOV8 INFERENCE
   ├── model.predict(image, conf=0.25, verbose=False)
   └── results → list of Detection(xyxy, conf, cls)

4. MAP DETECTIONS → PPE CHECKLIST
   ├── Với mỗi detection:
   │   └── cls_name = CLASS_NAMES[cls_id]
   │       └── Nếu cls_name in PPE_CLASS_MAP:
   │           └── ppe_class = PPE_CLASS_MAP[cls_name]
   │               └── Nếu conf ≥ THRESHOLDS[ppe_class]:
   │                   └── items[ppe_class] = {detected: True, confidence: conf}
   └── Items không được detect → {detected: False, confidence: 0.0}

5. DETERMINE OVERALL_PASS
   └── overall_pass = ALL(item.detected for item in items.values())

6. ANNOTATE IMAGE
   ├── Với mỗi item detected:
   │   ├── cv2.rectangle(img, bbox, color=GREEN, thickness=2)
   │   └── cv2.putText(img, f"{class_name} {conf:.0%}", ...)
   ├── Save annotated → static/results/{uuid}_annotated.jpg
   └── annotated_url = f"/static/results/{uuid}_annotated.jpg"

7. SAVE TO DATABASE
   └── INSERT INTO inspections:
       id, created_at, overall_pass,
       image_path, annotated_image_path,
       results_json (JSON stringify items),
       processing_time_ms

8. RETURN RESPONSE
   └── InspectionResponse(inspection_id, overall_pass, processing_time_ms,
                           annotated_image_url, items)
```

---

## 3. Database Design

**Table affected**: `inspections`

```sql
CREATE TABLE IF NOT EXISTS inspections (
    id                   TEXT PRIMARY KEY,
    created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    overall_pass         BOOLEAN NOT NULL,
    image_path           TEXT,
    annotated_image_path TEXT,
    results_json         TEXT NOT NULL,
    processing_time_ms   INTEGER
);

-- Index for dashboard queries
CREATE INDEX IF NOT EXISTS idx_inspections_created_at
    ON inspections(created_at DESC);
```

**INSERT on each check-ppe call:**
```sql
INSERT INTO inspections
    (id, created_at, overall_pass, image_path,
     annotated_image_path, results_json, processing_time_ms)
VALUES
    (:id, :now, :overall_pass, :image_path,
     :annotated_path, :results_json, :time_ms);
```

---

## 4. Implementation Details

### 4.1 Files

| File | Trách nhiệm |
|------|-------------|
| `backend/services/cv_engine.py` | YOLOv8 model load, inference, annotate |
| `backend/routers/check_ppe.py` | FastAPI router: validate, call service, return response |
| `backend/services/inspection_service.py` | Save inspection to DB |
| `backend/schemas/inspection.py` | Pydantic models: request/response |
| `backend/config.py` | Thresholds, paths, class mapping |

### 4.2 `cv_engine.py` — Core Class

```python
# backend/services/cv_engine.py

from ultralytics import YOLO
import cv2, numpy as np, uuid, time
from pathlib import Path

# === CONFIG ===
PPE_CLASS_MAP = {
    # Construction-PPE dataset class names → project class names
    "helmet":   "helmet",
    "vest":     "reflective_vest",
    "gloves":   "gloves",
    "boots":    "safety_boots",
    "goggles":  "safety_glasses",
    # SH17 dataset mappings
    "Helmet":        "helmet",
    "Safety-vest":   "reflective_vest",
    "Gloves":        "gloves",
    "Shoes":         "safety_boots",   # cần lọc cẩn thận
    "Glasses":       "safety_glasses", # cần lọc cẩn thận
}

THRESHOLDS = {
    "helmet":          0.50,
    "reflective_vest": 0.50,
    "gloves":          0.40,
    "safety_boots":    0.45,
    "safety_glasses":  0.40,
}

BBOX_COLOR   = (0, 200, 81)   # Xanh lá #00C851 (BGR)
BBOX_THICKNESS = 2
FONT          = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE    = 0.6
FONT_COLOR    = (255, 255, 255)


class CVEngine:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        self._warmup()

    def _warmup(self):
        """Chạy 1 lần khi khởi động để load model vào memory"""
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self.model.predict(dummy, verbose=False)

    def run(self, image_bytes: bytes, inspection_id: str) -> dict:
        """
        Main inference pipeline.
        Returns: dict với items, overall_pass, annotated_image_path
        """
        t_start = time.time()

        # 1. Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = self._resize(img, max_size=1280)

        # 2. Inference
        results = self.model.predict(img, conf=0.25, verbose=False)[0]

        # 3. Map → PPE checklist
        items = {k: {"detected": False, "confidence": 0.0} for k in THRESHOLDS}
        boxes_to_draw = []

        for box in results.boxes:
            cls_id   = int(box.cls[0])
            cls_name = self.model.names[cls_id]
            conf     = float(box.conf[0])

            ppe_class = PPE_CLASS_MAP.get(cls_name)
            if ppe_class and conf >= THRESHOLDS[ppe_class]:
                if not items[ppe_class]["detected"]:  # keep highest conf
                    items[ppe_class] = {"detected": True, "confidence": round(conf, 2)}
                    boxes_to_draw.append((box.xyxy[0].tolist(), ppe_class, conf))

        # 4. Overall pass
        overall_pass = all(v["detected"] for v in items.values())

        # 5. Annotate
        annotated_path = self._annotate(img, boxes_to_draw, inspection_id)

        processing_ms = int((time.time() - t_start) * 1000)

        return {
            "items": items,
            "overall_pass": overall_pass,
            "annotated_image_path": annotated_path,
            "processing_time_ms": processing_ms,
        }

    def _resize(self, img, max_size=1280):
        h, w = img.shape[:2]
        if max(h, w) <= max_size:
            return img
        scale = max_size / max(h, w)
        return cv2.resize(img, (int(w * scale), int(h * scale)))

    def _annotate(self, img, boxes, inspection_id: str) -> str:
        annotated = img.copy()
        for (x1, y1, x2, y2), ppe_class, conf in boxes:
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), BBOX_COLOR, BBOX_THICKNESS)
            label = f"{ppe_class} {conf:.0%}"
            cv2.putText(annotated, label, (x1, y1 - 8),
                        FONT, FONT_SCALE, FONT_COLOR, 2)

        out_path = f"static/results/{inspection_id}_annotated.jpg"
        Path("static/results").mkdir(parents=True, exist_ok=True)
        cv2.imwrite(out_path, annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return out_path
```

### 4.3 `check_ppe.py` — Router

```python
# backend/routers/check_ppe.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from services.cv_engine import CVEngine
from services.inspection_service import save_inspection
from schemas.inspection import InspectionResponse
import uuid

router = APIRouter(prefix="/api/v1", tags=["check-ppe"])
engine = CVEngine(model_path="./models_weights/ppe_yolov8n.pt")

ALLOWED_TYPES = {"image/jpeg", "image/png"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

@router.post("/check-ppe", response_model=InspectionResponse)
async def check_ppe(image: UploadFile = File(...)):
    # Validate
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file format. Only JPEG and PNG accepted.")

    image_bytes = await image.read()
    if len(image_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(413, "File too large. Maximum size is 10MB.")

    # Inference
    inspection_id = str(uuid.uuid4())
    result = engine.run(image_bytes, inspection_id)

    # Save
    save_inspection(inspection_id, result)

    return InspectionResponse(
        inspection_id=inspection_id,
        overall_pass=result["overall_pass"],
        processing_time_ms=result["processing_time_ms"],
        annotated_image_url=f"/{result['annotated_image_path']}",
        items=result["items"],
    )
```

### 4.4 Pydantic Schemas

```python
# backend/schemas/inspection.py

from pydantic import BaseModel
from typing import Dict

class PPEItem(BaseModel):
    detected: bool
    confidence: float

class InspectionResponse(BaseModel):
    inspection_id: str
    overall_pass: bool
    processing_time_ms: int
    annotated_image_url: str
    items: Dict[str, PPEItem]
```

### 4.5 Model Loading Strategy

```python
# backend/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import check_ppe, inspections, stats
from database import create_tables

app = FastAPI(title="Safety PPE Checker API")

@app.on_event("startup")
async def startup():
    create_tables()                    # Tạo DB tables nếu chưa có
    # CVEngine được init trong router module (module-level singleton)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(check_ppe.router)
app.include_router(inspections.router)
app.include_router(stats.router)
```

---

## 5. Security & Performance

| Concern | Solution |
|---------|----------|
| File type bypass | Kiểm tra cả Content-Type header VÀ magic bytes nếu cần |
| Large file DoS | Max 10MB client-side + server-side check |
| Model loading time | Load 1 lần khi startup, dùng singleton pattern |
| Inference speed | YOLOv8n < 1s trên CPU thông thường |
| Disk space | Static files: giữ 7 ngày, auto-delete cũ nếu cần |
| CORS | `CORSMiddleware` allow `http://localhost:3000` |

```python
# CORS setup trong main.py
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6. Mapping to User Stories

| API / Feature | User Story |
|--------------|------------|
| Detect `helmet` class | [US-CV-001](../../01_product_requirements/cv-engine/US-CV-001.md) |
| Detect `reflective_vest`, `gloves`, `safety_boots`, `safety_glasses` | [US-CV-002](../../01_product_requirements/cv-engine/US-CV-002.md) |
| `overall_pass` + JSON response + DB save | [US-CV-003](../../01_product_requirements/cv-engine/US-CV-003.md) |
| Annotated image với bounding boxes | [US-CV-004](../../01_product_requirements/cv-engine/US-CV-004.md) |

---

## 7. Training Notes (không phải runtime spec)

```bash
# Fine-tune YOLOv8n trên Construction-PPE dataset
yolo detect train \
  data=construction-ppe.yaml \
  model=yolov8n.pt \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  name=ppe_v1

# Kết quả model lưu tại:
# runs/detect/ppe_v1/weights/best.pt
# → Copy về: backend/models_weights/ppe_yolov8n.pt
```

---

> **Changelog**
> | Version | Date | Changes |
> |---------|------|---------|
> | v1.0 | 2026-03-15 | Initial tech spec |
