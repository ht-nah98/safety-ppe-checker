# Technical Specification: TP-DSH-001
## Dashboard — Lịch sử, Thống kê & Export APIs

> **Status**: Draft
> **Linked Epic**: [EPIC-DSH-001](../../01_product_requirements/dashboard/EPIC-DSH-001.md)
> **Linked Stories**: US-DSH-001, US-DSH-002, US-DSH-003
> **Source Files**: `backend/routers/inspections.py`, `backend/routers/stats.py`, `frontend/src/pages/DashboardPage.jsx`

---

## 1. Overview

Dashboard module cung cấp 3 API endpoints để lấy dữ liệu lịch sử và thống kê từ bảng `inspections`, và 1 endpoint export CSV. Frontend dùng các API này để render trang Dashboard gồm: 4 summary cards, 1 bar chart vi phạm theo loại PPE, và bảng lịch sử có thể xem chi tiết.

---

## 2. API Specifications

### 2.1 Lấy danh sách lịch sử kiểm tra — US-DSH-001

**Endpoint**: `GET /api/v1/inspections`

**Query Parameters**:
| Param | Type | Default | Mô tả |
|-------|------|---------|-------|
| `limit` | int | 20 | Số records trả về |
| `offset` | int | 0 | Bỏ qua N records đầu (pagination) |

**Response 200 OK**:
```json
{
  "total": 247,
  "inspections": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "created_at": "2026-03-15T09:23:45",
      "overall_pass": false,
      "violated_items": ["gloves", "safety_glasses"],
      "annotated_image_url": "/static/results/3fa85f64_annotated.jpg"
    },
    {
      "id": "7cb12a33-...",
      "created_at": "2026-03-15T09:18:12",
      "overall_pass": true,
      "violated_items": [],
      "annotated_image_url": "/static/results/7cb12a33_annotated.jpg"
    }
  ]
}
```

**Logic Flow**:
```
1. Parse query params (limit, offset) — validate: limit ≤ 100
2. SELECT id, created_at, overall_pass, results_json, annotated_image_path
   FROM inspections ORDER BY created_at DESC
   LIMIT :limit OFFSET :offset
3. SELECT COUNT(*) FROM inspections  (để trả total)
4. Với mỗi record:
   └── Parse results_json → extract violated_items = [k for k,v where not v.detected]
5. Return { total, inspections[] }
```

---

### 2.2 Lấy chi tiết 1 inspection

**Endpoint**: `GET /api/v1/inspections/{inspection_id}`

**Response 200 OK**:
```json
{
  "id": "3fa85f64-...",
  "created_at": "2026-03-15T09:23:45",
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

**Logic Flow**:
```
1. SELECT * FROM inspections WHERE id = :inspection_id
2. Nếu không tìm thấy → 404 Not Found
3. Parse results_json → items dict
4. Return full inspection detail
```

---

### 2.3 Thống kê tổng quan — US-DSH-002

**Endpoint**: `GET /api/v1/stats`

**Response 200 OK**:
```json
{
  "total": 247,
  "pass_count": 198,
  "fail_count": 49,
  "compliance_rate": 0.802,
  "violations_by_class": {
    "helmet":          12,
    "reflective_vest":  8,
    "gloves":          45,
    "safety_boots":    15,
    "safety_glasses":  32
  }
}
```

**Logic Flow**:
```
1. Đếm tổng + pass + fail:
   SELECT
     COUNT(*) as total,
     SUM(CASE WHEN overall_pass = 1 THEN 1 ELSE 0 END) as pass_count
   FROM inspections

2. Tính compliance_rate = pass_count / total (0 nếu total = 0)

3. Đếm violations per class:
   SELECT results_json FROM inspections WHERE overall_pass = 0
   → Với mỗi record:
       parse results_json → items
       Với mỗi item không detected: violations_by_class[class] += 1

4. Return stats object
```

**Performance note**: Với ≤ 1,000 records (demo scale), scan toàn bộ là OK. Production cần aggregate columns hoặc materialized view.

---

### 2.4 Export CSV — US-DSH-003

**Endpoint**: `GET /api/v1/inspections/export`

**Response**:
- Status: 200 OK
- Content-Type: `text/csv; charset=utf-8-sig`
- Content-Disposition: `attachment; filename="ppe-inspections-{date}.csv"`

**CSV Format**:
```
Thời gian,Kết quả,Mũ bảo hộ,Áo phản quang,Găng tay,Giày bảo hộ,Kính bảo hộ
2026-03-15 09:23:45,FAIL,Có,Có,Không,Có,Không
2026-03-15 09:18:12,PASS,Có,Có,Có,Có,Có
```

**Logic Flow**:
```
1. SELECT * FROM inspections ORDER BY created_at DESC
2. Với mỗi record:
   parse results_json → items
   row = [
     created_at.strftime('%Y-%m-%d %H:%M:%S'),
     "PASS" if overall_pass else "FAIL",
     "Có" if items.helmet.detected else "Không",
     "Có" if items.reflective_vest.detected else "Không",
     "Có" if items.gloves.detected else "Không",
     "Có" if items.safety_boots.detected else "Không",
     "Có" if items.safety_glasses.detected else "Không",
   ]
3. StreamingResponse với CSV content
4. utf-8-sig encoding (BOM) để Excel hiển thị tiếng Việt đúng
```

---

## 3. Database Design

**Table used**: `inspections` (đã định nghĩa trong TP-CV-001)

**Queries chi tiết:**

```sql
-- 2.1: Danh sách lịch sử
SELECT id, created_at, overall_pass, results_json, annotated_image_path
FROM inspections
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;

-- Count total
SELECT COUNT(*) FROM inspections;

-- 2.3: Stats cơ bản
SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN overall_pass = 1 THEN 1 ELSE 0 END) AS pass_count,
    SUM(CASE WHEN overall_pass = 0 THEN 1 ELSE 0 END) AS fail_count
FROM inspections;

-- 2.3: Lấy data tính violations by class
SELECT results_json
FROM inspections
WHERE overall_pass = 0;

-- 2.4: Export toàn bộ
SELECT id, created_at, overall_pass, results_json
FROM inspections
ORDER BY created_at DESC;
```

---

## 4. Implementation Details

### 4.1 `routers/inspections.py`

```python
# backend/routers/inspections.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from services.inspection_service import (
    get_inspections_list, get_inspection_detail,
    get_stats_data, generate_csv
)
import json
from datetime import date

router = APIRouter(prefix="/api/v1", tags=["inspections"])

@router.get("/inspections")
def list_inspections(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    if limit > 100:
        limit = 100
    return get_inspections_list(db, limit, offset)

@router.get("/inspections/export")
def export_csv(db: Session = Depends(get_db)):
    csv_content = generate_csv(db)
    filename = f"ppe-inspections-{date.today().isoformat()}.csv"
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/inspections/{inspection_id}")
def get_inspection(inspection_id: str, db: Session = Depends(get_db)):
    record = get_inspection_detail(db, inspection_id)
    if not record:
        raise HTTPException(404, "Inspection not found")
    return record

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return get_stats_data(db)
```

### 4.2 `services/inspection_service.py`

```python
# backend/services/inspection_service.py
import json, csv, io
from datetime import datetime
from models.inspection import Inspection
from sqlalchemy.orm import Session
from sqlalchemy import func

PPE_CLASSES = ["helmet", "reflective_vest", "gloves", "safety_boots", "safety_glasses"]
PPE_LABELS_VI = {
    "helmet":          "Mũ bảo hộ",
    "reflective_vest": "Áo phản quang",
    "gloves":          "Găng tay",
    "safety_boots":    "Giày bảo hộ",
    "safety_glasses":  "Kính bảo hộ",
}

def save_inspection(db: Session, inspection_id: str, result: dict):
    record = Inspection(
        id=inspection_id,
        created_at=datetime.utcnow(),
        overall_pass=result["overall_pass"],
        annotated_image_path=result["annotated_image_path"],
        results_json=json.dumps(result["items"]),
        processing_time_ms=result["processing_time_ms"],
    )
    db.add(record)
    db.commit()

def get_inspections_list(db: Session, limit: int, offset: int):
    total = db.query(func.count(Inspection.id)).scalar()
    records = (db.query(Inspection)
                 .order_by(Inspection.created_at.desc())
                 .limit(limit).offset(offset).all())
    inspections = []
    for r in records:
        items = json.loads(r.results_json)
        violated = [k for k, v in items.items() if not v["detected"]]
        inspections.append({
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "overall_pass": r.overall_pass,
            "violated_items": violated,
            "annotated_image_url": f"/static/results/{r.id}_annotated.jpg",
        })
    return {"total": total, "inspections": inspections}

def get_inspection_detail(db: Session, inspection_id: str):
    r = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not r:
        return None
    return {
        "id": r.id,
        "created_at": r.created_at.isoformat(),
        "overall_pass": r.overall_pass,
        "processing_time_ms": r.processing_time_ms,
        "annotated_image_url": f"/static/results/{r.id}_annotated.jpg",
        "items": json.loads(r.results_json),
    }

def get_stats_data(db: Session):
    total = db.query(func.count(Inspection.id)).scalar() or 0
    pass_count = db.query(func.count(Inspection.id)).filter(
        Inspection.overall_pass == True).scalar() or 0
    fail_count = total - pass_count
    compliance_rate = round(pass_count / total, 3) if total > 0 else 0.0

    # violations by class
    violations = {k: 0 for k in PPE_CLASSES}
    fail_records = db.query(Inspection.results_json).filter(
        Inspection.overall_pass == False).all()
    for (results_json,) in fail_records:
        items = json.loads(results_json)
        for cls in PPE_CLASSES:
            if not items.get(cls, {}).get("detected", True):
                violations[cls] += 1

    return {
        "total": total,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "compliance_rate": compliance_rate,
        "violations_by_class": violations,
    }

def generate_csv(db: Session) -> str:
    records = db.query(Inspection).order_by(Inspection.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    # Header
    writer.writerow(["Thời gian", "Kết quả"] + list(PPE_LABELS_VI.values()))
    # Rows
    for r in records:
        items = json.loads(r.results_json)
        row = [
            r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "PASS" if r.overall_pass else "FAIL",
        ] + ["Có" if items.get(k, {}).get("detected") else "Không" for k in PPE_CLASSES]
        writer.writerow(row)
    return "\ufeff" + output.getvalue()  # BOM cho Excel tiếng Việt
```

### 4.3 Frontend — DashboardPage

```jsx
// frontend/src/pages/DashboardPage.jsx
import { useState, useEffect } from 'react';
import { getStats, getInspections, getExportUrl } from '../api/ppe';
import { StatsCards } from '../components/StatsCards';
import { ViolationChart } from '../components/ViolationChart';
import { InspectionTable } from '../components/InspectionTable';

export function DashboardPage() {
  const [stats, setStats]               = useState(null);
  const [inspections, setInspections]   = useState([]);
  const [total, setTotal]               = useState(0);
  const [loading, setLoading]           = useState(true);

  useEffect(() => {
    Promise.all([getStats(), getInspections(20, 0)])
      .then(([s, i]) => {
        setStats(s);
        setInspections(i.inspections);
        setTotal(i.total);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1>Dashboard — Lịch sử kiểm tra PPE</h1>

      {stats && <StatsCards stats={stats} />}
      {stats && <ViolationChart data={stats.violations_by_class} />}

      <a href={getExportUrl()} download>
        <button>⬇ Export CSV</button>
      </a>

      <InspectionTable inspections={inspections} total={total} />
    </div>
  );
}
```

### 4.4 ViolationChart — Chart.js

```jsx
// frontend/src/components/ViolationChart.jsx
import { Bar } from 'react-chartjs-2';

const PPE_LABELS_VI = {
  helmet: 'Mũ bảo hộ',
  reflective_vest: 'Áo phản quang',
  gloves: 'Găng tay',
  safety_boots: 'Giày bảo hộ',
  safety_glasses: 'Kính bảo hộ',
};

export function ViolationChart({ data }) {
  const chartData = {
    labels: Object.keys(data).map(k => PPE_LABELS_VI[k]),
    datasets: [{
      label: 'Số lượt vi phạm',
      data: Object.values(data),
      backgroundColor: 'rgba(255, 53, 71, 0.7)', // đỏ
      borderRadius: 6,
    }],
  };
  return <Bar data={chartData} options={{ responsive: true }} />;
}
```

### 4.5 Seed Demo Data Script

```python
# scripts/seed_demo_data.py
# Chạy 1 lần trước demo để có 30 inspections giả lập

import sqlite3, json, uuid
from datetime import datetime, timedelta
import random

DB_PATH = "backend/ppe_checker.db"
PPE_CLASSES = ["helmet", "reflective_vest", "gloves", "safety_boots", "safety_glasses"]

def random_inspection(offset_hours):
    # 80% pass rate để demo trông thực tế
    num_violations = random.choices([0, 1, 2], weights=[80, 15, 5])[0]
    violated = random.sample(PPE_CLASSES, num_violations)
    items = {}
    for cls in PPE_CLASSES:
        if cls in violated:
            items[cls] = {"detected": False, "confidence": 0.0}
        else:
            items[cls] = {"detected": True,  "confidence": round(random.uniform(0.65, 0.97), 2)}
    return {
        "id": str(uuid.uuid4()),
        "created_at": (datetime.now() - timedelta(hours=offset_hours)).isoformat(),
        "overall_pass": len(violated) == 0,
        "results_json": json.dumps(items),
        "processing_time_ms": random.randint(800, 2500),
    }

conn = sqlite3.connect(DB_PATH)
for i in range(30):
    r = random_inspection(offset_hours=i * 0.5)
    conn.execute("""
        INSERT INTO inspections (id, created_at, overall_pass, results_json, processing_time_ms)
        VALUES (?, ?, ?, ?, ?)
    """, (r["id"], r["created_at"], r["overall_pass"], r["results_json"], r["processing_time_ms"]))
conn.commit()
conn.close()
print("✅ Seeded 30 demo inspections")
```

---

## 5. Security & Performance

| Concern | Solution |
|---------|----------|
| SQL injection | SQLAlchemy ORM — parameterized queries |
| Large export | StreamingResponse — không load toàn bộ vào memory |
| Pagination | `limit` cap at 100, `offset` cho infinite scroll |
| CSV encoding | utf-8-sig (BOM) để Excel hiển thị tiếng Việt đúng |
| Stats recalculation | OK cho demo scale (≤ 1,000 rows) |

---

## 6. Mapping to User Stories

| API / Feature | User Story |
|--------------|------------|
| `GET /inspections` + InspectionTable component | [US-DSH-001](../../01_product_requirements/dashboard/US-DSH-001.md) |
| `GET /stats` + StatsCards + ViolationChart | [US-DSH-002](../../01_product_requirements/dashboard/US-DSH-002.md) |
| `GET /inspections/export` + CSV download | [US-DSH-003](../../01_product_requirements/dashboard/US-DSH-003.md) |

---

> **Changelog**
> | Version | Date | Changes |
> |---------|------|---------|
> | v1.0 | 2026-03-15 | Initial tech spec |
