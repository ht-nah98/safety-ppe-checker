# Kiến trúc hệ thống: Safety PPE Checker

> **Status**: Draft
> **Created**: 2026-03-15
> **Version**: v1.0

---

## Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc tổng thể](#2-kiến-trúc-tổng-thể)
3. [Data Flow](#3-data-flow)
4. [Cấu trúc Source Code](#4-cấu-trúc-source-code)
5. [Database Schema](#5-database-schema)
6. [Tech Stack chi tiết](#6-tech-stack-chi-tiết)
7. [Deployment — Docker Compose](#7-deployment--docker-compose)
8. [API Overview](#8-api-overview)
9. [Modules và Dependencies](#9-modules-và-dependencies)

---

## 1. Tổng quan

### 1.1 Mục đích

Safety PPE Checker là hệ thống web demo 3-tier đơn giản:
- **Frontend**: React SPA cho công nhân upload/chụp ảnh và xem kết quả
- **Backend**: FastAPI REST API xử lý inference, lưu trữ, thống kê
- **CV Engine**: Module Python chạy YOLOv8 inference, annotate ảnh

### 1.2 Quy mô hệ thống (Demo)

| Thông số | Giá trị |
|----------|---------|
| Concurrent users | ≤ 10 (demo) |
| Requests/ngày | ≤ 200 |
| Thời gian xử lý | < 3 giây / request |
| Storage | ≤ 2 GB (ảnh + model) |
| Availability | Không cần SLA — chỉ cần ổn trong demo |

### 1.3 Tech Stack

| Thành phần | Công nghệ | Version |
|-----------|-----------|---------|
| **Backend** | Python / FastAPI | Python 3.11+, FastAPI 0.110+ |
| **CV Engine** | Ultralytics YOLOv8n | 8.x |
| **Database** | SQLite (dev) | Built-in Python |
| **Image Processing** | OpenCV (cv2) | 4.x |
| **Frontend** | React + Vite | React 18, Vite 5 |
| **CSS** | Tailwind CSS | 3.x |
| **Charts** | Chart.js (react-chartjs-2) | 4.x |
| **Deployment** | Docker + Docker Compose | 24.x |
| **Static Files** | FastAPI StaticFiles | — |

---

## 2. Kiến trúc tổng thể

```
┌──────────────────────────────────────────────────────────────────┐
│                        BROWSER (Client)                           │
│                                                                    │
│   ┌────────────────────────────────────────────────────────────┐  │
│   │                React SPA (Port 3000)                        │  │
│   │                                                             │  │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │  │
│   │   │  Upload Page │  │ Results Page │  │   Dashboard  │    │  │
│   │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │  │
│   └──────────┼─────────────────┼─────────────────┼────────────┘  │
└──────────────┼─────────────────┼─────────────────┼───────────────┘
               │ HTTP REST        │                 │
               │ multipart/form   │ GET JSON        │ GET JSON
               ▼                 ▼                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Port 8000)                      │
│                                                                    │
│  ┌─────────────────┐  ┌────────────────┐  ┌────────────────────┐ │
│  │  POST /check-ppe│  │ GET /inspections│  │    GET /stats      │ │
│  │  (CV Engine     │  │ GET /inspections│  │ GET /export?csv    │ │
│  │   trigger)      │  │ /:id            │  │                    │ │
│  └────────┬────────┘  └────────┬───────┘  └────────┬───────────┘ │
│           │                    │                    │             │
│  ┌────────▼────────┐  ┌────────▼───────────────────▼───────────┐ │
│  │   CV Engine     │  │            Database Layer               │ │
│  │  (YOLOv8n       │  │         SQLite / SQLAlchemy             │ │
│  │   inference +   │  │                                         │ │
│  │   annotate)     │  │  inspections table                      │ │
│  └────────┬────────┘  └─────────────────────────────────────────┘ │
│           │                                                        │
│  ┌────────▼────────┐                                              │
│  │  Static Files   │  ← /static/results/{uuid}_annotated.jpg     │
│  │  (annotated     │                                              │
│  │   images)       │                                              │
│  └─────────────────┘                                              │
└──────────────────────────────────────────────────────────────────┘
```

### 2.1 Communication Patterns

| Pattern | Mục đích |
|---------|----------|
| REST HTTP (JSON) | Frontend ↔ Backend — mọi API call |
| multipart/form-data | Upload file ảnh từ Frontend → Backend |
| StaticFiles HTTP | Backend serve annotated images về Frontend |
| Sync (no queue) | CV inference đồng bộ — đủ cho demo |

---

## 3. Data Flow

### 3.1 Luồng kiểm tra PPE (Happy Path)

```
User                  Frontend              Backend              CV Engine        DB
 │                       │                     │                     │            │
 │  Upload / Capture      │                     │                     │            │
 │──────────────────────>│                     │                     │            │
 │                        │  POST /check-ppe    │                     │            │
 │                        │  (multipart image)  │                     │            │
 │                        │────────────────────>│                     │            │
 │                        │                     │  run_inference(img)  │            │
 │                        │                     │────────────────────>│            │
 │                        │                     │                     │ YOLOv8n    │
 │                        │                     │                     │ forward()  │
 │                        │                     │  detections[]       │            │
 │                        │                     │<────────────────────│            │
 │                        │                     │  annotate_image()   │            │
 │                        │                     │────────────────────>│            │
 │                        │                     │  annotated_path     │            │
 │                        │                     │<────────────────────│            │
 │                        │                     │  save inspection    │            │
 │                        │                     │────────────────────────────────>│
 │                        │                     │  inspection_id      │            │
 │                        │                     │<────────────────────────────────│
 │                        │  JSON response      │                     │            │
 │                        │<────────────────────│                     │            │
 │  Show Results page     │                     │                     │            │
 │<──────────────────────│                     │                     │            │
 │                        │  GET /static/...jpg │                     │            │
 │                        │────────────────────>│                     │            │
 │                        │  image binary       │                     │            │
 │                        │<────────────────────│                     │            │
```

### 3.2 Luồng xem Dashboard

```
Frontend ──GET /stats──────────────────────> Backend
         <──{ total, pass, fail, by_class }──

Frontend ──GET /inspections?limit=20───────> Backend ──SELECT──> DB
         <──{ inspections: [...], total: N }──────────<──────────
```

---

## 4. Cấu trúc Source Code

```
safety-ppe-checker/
│
├── backend/                        # FastAPI application
│   ├── main.py                     # App entry point, router registration
│   ├── config.py                   # Settings (thresholds, paths, DB URL)
│   ├── database.py                 # SQLAlchemy engine & session
│   │
│   ├── models/
│   │   └── inspection.py           # SQLAlchemy ORM model
│   │
│   ├── schemas/
│   │   ├── inspection.py           # Pydantic request/response schemas
│   │   └── stats.py                # Stats response schema
│   │
│   ├── routers/
│   │   ├── check_ppe.py            # POST /api/v1/check-ppe
│   │   ├── inspections.py          # GET /api/v1/inspections, /:id, /export
│   │   └── stats.py                # GET /api/v1/stats
│   │
│   ├── services/
│   │   ├── cv_engine.py            # YOLOv8 inference + annotate
│   │   └── inspection_service.py   # Business logic: save, query, export
│   │
│   ├── static/
│   │   └── results/                # Annotated images output
│   │
│   ├── data/                       # Training data (gitignored)
│   │   ├── raw/
│   │   ├── processed/
│   │   └── demo/
│   │
│   ├── models_weights/             # YOLOv8 .pt files
│   │   └── ppe_yolov8n.pt
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                       # React application
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx                 # Routes
│   │   │
│   │   ├── pages/
│   │   │   ├── HomePage.jsx        # Chọn Upload hoặc Webcam
│   │   │   ├── UploadPage.jsx      # Upload flow
│   │   │   ├── CameraPage.jsx      # Webcam capture flow
│   │   │   ├── ResultsPage.jsx     # Kết quả kiểm tra
│   │   │   └── DashboardPage.jsx   # Lịch sử + thống kê
│   │   │
│   │   ├── components/
│   │   │   ├── PPEChecklist.jsx    # 5-item checklist component
│   │   │   ├── VerdictHeader.jsx   # PASS/FAIL header
│   │   │   ├── StatsCards.jsx      # 4 summary cards
│   │   │   ├── ViolationChart.jsx  # Bar chart (Chart.js)
│   │   │   └── InspectionTable.jsx # History table
│   │   │
│   │   └── api/
│   │       └── ppe.js              # API call functions
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── docker-compose.yml              # Chạy cả backend + frontend
└── scripts/
    └── seed_demo_data.py           # Tạo 30 inspections giả lập
```

---

## 5. Database Schema

### Table: `inspections`

```sql
CREATE TABLE inspections (
    id                  TEXT PRIMARY KEY,       -- UUID v4
    created_at          DATETIME NOT NULL,      -- Thời gian kiểm tra
    overall_pass        BOOLEAN NOT NULL,       -- True = PASS, False = FAIL
    image_path          TEXT,                   -- Path ảnh gốc
    annotated_image_path TEXT,                  -- Path ảnh annotated
    results_json        TEXT NOT NULL,          -- JSON string toàn bộ kết quả
    processing_time_ms  INTEGER                 -- Thời gian inference (ms)
);
```

**`results_json` structure:**
```json
{
  "items": {
    "helmet":          { "detected": true,  "confidence": 0.94 },
    "reflective_vest": { "detected": true,  "confidence": 0.89 },
    "gloves":          { "detected": false, "confidence": 0.0  },
    "safety_boots":    { "detected": true,  "confidence": 0.76 },
    "safety_glasses":  { "detected": false, "confidence": 0.0  }
  }
}
```

### Key Queries

```sql
-- Lấy danh sách lịch sử
SELECT id, created_at, overall_pass, results_json
FROM inspections
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;

-- Thống kê tổng quan
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN overall_pass = 1 THEN 1 ELSE 0 END) as pass_count,
    SUM(CASE WHEN overall_pass = 0 THEN 1 ELSE 0 END) as fail_count
FROM inspections;
```

---

## 6. Tech Stack chi tiết

### Backend Python packages

```
# requirements.txt
fastapi==0.110.0
uvicorn[standard]==0.29.0
python-multipart==0.0.9      # File upload
sqlalchemy==2.0.29           # ORM
ultralytics==8.2.0           # YOLOv8
opencv-python==4.9.0.80      # Image annotation
pillow==10.3.0               # Image processing
pydantic==2.7.0              # Schemas
python-jose==3.3.0           # UUID generation
aiofiles==23.2.1             # Async file operations
```

### Frontend packages

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.22.0",
  "react-webcam": "^7.2.0",
  "chart.js": "^4.4.2",
  "react-chartjs-2": "^5.2.0",
  "axios": "^1.6.8",
  "tailwindcss": "^3.4.3"
}
```

---

## 7. Deployment — Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/static:/app/static
      - ./backend/data:/app/data
      - ./backend/models_weights:/app/models_weights
    environment:
      - DATABASE_URL=sqlite:///./ppe_checker.db
      - MODEL_PATH=./models_weights/ppe_yolov8n.pt

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

**Run:**
```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 8. API Overview

| Method | Endpoint | Mô tả | TP |
|--------|----------|-------|----|
| POST | `/api/v1/check-ppe` | Nhận ảnh → inference → trả kết quả | TP-CV-001 |
| GET | `/api/v1/inspections` | Danh sách lịch sử (paginated) | TP-DSH-001 |
| GET | `/api/v1/inspections/{id}` | Chi tiết 1 inspection | TP-DSH-001 |
| GET | `/api/v1/inspections/export` | Export CSV | TP-DSH-001 |
| GET | `/api/v1/stats` | Thống kê tổng quan + vi phạm | TP-DSH-001 |
| GET | `/static/results/{filename}` | Serve annotated images | — |

---

## 9. Modules và Dependencies

```
EPIC-CV-001 (CV Engine)
└── TP-CV-001: check-ppe API + inference + DB write
        ↓ provides data for
EPIC-DSH-001 (Dashboard)
└── TP-DSH-001: inspections list + stats + export APIs
        ↑ consumed by
EPIC-WEB-001 (Web Interface)
└── TP-WEB-001: React app calling all backend APIs
```

| Module | File chính | Phụ thuộc |
|--------|-----------|-----------|
| CV Engine | `services/cv_engine.py` | ultralytics, opencv-python |
| Inspection Service | `services/inspection_service.py` | sqlalchemy, cv_engine |
| Check PPE Router | `routers/check_ppe.py` | inspection_service |
| Inspections Router | `routers/inspections.py` | inspection_service |
| Stats Router | `routers/stats.py` | inspection_service |
| Frontend API | `src/api/ppe.js` | axios, backend running |

---

## Tài liệu liên quan

- [PRD](../01_product_requirements/prd/PRD-safety-ppe-checker.md)
- [TP-CV-001 — CV Engine API](./cv-engine/TP-CV-001.md)
- [TP-WEB-001 — Web Interface](./web-interface/TP-WEB-001.md)
- [TP-DSH-001 — Dashboard APIs](./dashboard/TP-DSH-001.md)
- [DATA-STRATEGY](../06_research/DATA-STRATEGY.md)

---

> **Changelog**
> | Version | Date | Changes |
> |---------|------|---------|
> | v1.0 | 2026-03-15 | Initial architecture |
