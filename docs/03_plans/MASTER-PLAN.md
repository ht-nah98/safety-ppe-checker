# MASTER PLAN: PPE Compliance Detection Demo
## Tự động đánh giá tuân thủ trang phục bảo hộ qua ảnh chụp

> **Saved**: 2026-03-15
> **Status**: In Planning
> **Timeline**: 2026-03-15 → 2026-04-12 (4 tuần)
> **Purpose**: Demo website trình bày khả năng AI detect PPE cho công nhân điện lực

---

## MỤC LỤC

1. [Làm rõ & cải thiện đề tài](#phần-1--làm-rõ--cải-thiện-đề-tài)
2. [Sample Data — Nguồn dữ liệu](#phần-2--sample-data--nguồn-dữ-liệu)
3. [Project Setup](#phần-3--project-setup)
4. [Product Documentation](#phần-4--product-documentation-tuần-1-ngày-1-3)
5. [Technical Design](#phần-5--technical-design-tuần-1-ngày-3-5)
6. [Build Plan — 3 Sprints](#phần-6--build-plan-tuần-2-4)
7. [Testing Plan](#phần-7--testing-plan)
8. [Document Map](#phần-8--document-map-tổng-thể)
9. [Timeline Tổng quan](#phần-9--timeline-tổng-quan)

---

## PHẦN 1 — LÀM RÕ & CẢI THIỆN ĐỀ TÀI

### 1.1 Vấn đề với mô tả ban đầu

| Hiện tại | Cải thiện |
|----------|-----------|
| "Sửa chữa điện" — quá rộng | Làm rõ: **công nhân điện lực** thực hiện **sửa chữa/bảo trì đường dây & tủ điện** |
| "AI đánh giá" — mơ hồ | Detect + verify từng hạng mục PPE, trả về pass/fail từng mục + tổng thể |
| Demo chưa rõ scope | Web app demo: upload ảnh / chụp camera / xem lịch sử |
| YOLOv8 + pose estimation | Demo: YOLOv8 nano đủ dùng — pose estimation để Phase 2 |

### 1.2 Problem Statement (chuẩn hóa)

```
Nhân viên điện lực (công nhân + giám sát)
cần một cách để XÁC NHẬN đầy đủ trang bị PPE TRƯỚC KHI bắt đầu công việc
vì vi phạm PPE là nguyên nhân hàng đầu gây tai nạn lao động ngành điện.

Hiện tại, giám sát viên phải kiểm tra thủ công từng người,
gây tốn thời gian, dễ bỏ sót, và không có audit trail.
```

### 1.3 Demo Scope

**IN SCOPE (Demo):**
- Upload ảnh hoặc chụp từ webcam
- AI detect 5 hạng mục PPE: mũ bảo hộ, áo phản quang, găng tay, giày bảo hộ, kính bảo hộ
- Hiển thị kết quả: bounding box + pass/fail từng mục + tổng kết
- Lưu lịch sử kiểm tra (session)
- Dashboard: số lượt pass/fail, biểu đồ vi phạm theo loại PPE

**OUT OF SCOPE (Demo — để Phase 2):**
- Pose estimation (verify PPE đúng vị trí)
- Nhận diện danh tính nhân viên
- Tích hợp hệ thống HR/chấm công
- Mobile app native
- Multi-job-type checklist
- Real-time video stream

---

## PHẦN 2 — SAMPLE DATA — NGUỒN DỮ LIỆU

> Đây là bước quan trọng trước khi build CV Engine. Cần chuẩn bị data trước Sprint 1.
> **Chi tiết đầy đủ**: xem [DATA-STRATEGY.md](../06_research/DATA-STRATEGY.md)

### 2.1 Tổng hợp các dataset đã nghiên cứu

*(Đã research và phân tích đầy đủ 6 datasets — xem DATA-STRATEGY.md Sections 2–3)*

| Dataset | Images | 5 Classes đủ? | Negative classes? | Format | License |
|---------|-------:|:-------------:|:-----------------:|--------|---------|
| **Construction-PPE (Ultralytics)** | 1,416 | ✅ Đủ 5 | ✅ Có (no_helmet...) | YOLOv8 native | AGPL-3.0 |
| **SH17 (Kaggle)** | 8,099 | ⚠️ 5/5 nhưng Shoes/Glasses rộng | ❌ Không | Verify | CC BY-NC-SA 4.0 |
| Mendeley PPE 2025 | 2,286 | ❌ Chỉ 2/5 | ❌ | YOLOv8 | CC BY 4.0 |
| PPE COCO (Kaggle) | 44,000 | ✅ | ❌ | COCO JSON | Apache 2.0 |
| SHWD (GitHub) | 7,581 | ❌ Chỉ 1/5 | ✅ (head) | VOC XML | MIT |

### 2.2 Quyết định dataset — CHÍNH THỨC

**Chiến lược 2-tier:**

**TIER 1 — PRIMARY: Construction-PPE (Ultralytics)** ⭐
- Lý do: Dataset DUY NHẤT có đủ 5 class + negative classes (no_helmet, no_gloves...)
- YOLOv8 native — tự động download, không cần setup thêm
- Dùng ngay từ Sprint 1, Ngày 1
- Download: `yolo detect train data=construction-ppe.yaml model=yolov8n.pt epochs=1`

**TIER 2 — SUPPLEMENT: SH17 Dataset (Kaggle)** ⭐
- Lý do: 8,099 ảnh chất lượng cao → tăng accuracy gloves/glasses
- Dùng Sprint 1, Ngày 2–3 nếu accuracy chưa đạt ≥ 80%
- Download: `kaggle datasets download -d mugheesahmad/sh17-dataset-for-ppe-detection`

**SKIP:** SHWD (chỉ helmet), Mendeley (chỉ 2 class), COCO PPE (để Phase 2)

### 2.3 Class Mapping chính thức

| Class project | ← Construction-PPE | ← SH17 |
|--------------|-------------------|--------|
| `helmet` | `helmet` | `Helmet` |
| `reflective_vest` | `vest` | `Safety-vest` |
| `gloves` | `gloves` | `Gloves` |
| `safety_boots` | `boots` | `Shoes` ⚠️ cần lọc |
| `safety_glasses` | `goggles` | `Glasses` ⚠️ cần lọc |

### 2.4 Test Images cho Demo

| Loại | Số lượng | Nguồn gợi ý |
|------|----------|-------------|
| PASS — đủ 5 PPE, ánh sáng tốt | 5 ảnh | Test split của Construction-PPE |
| FAIL — thiếu mũ | 3 ảnh | Google: "electrical worker no helmet" |
| FAIL — thiếu găng tay | 3 ảnh | Construction-PPE test split (FAIL cases) |
| FAIL — thiếu kính | 3 ảnh | Construction-PPE test split |
| FAIL — thiếu nhiều mục | 3 ảnh | Tự tạo từ dataset |
| Edge case — ánh sáng kém | 2 ảnh | Google: "worker dark lighting" |

**Từ khóa tìm kiếm demo images:**
- Google Images: "electrical worker full PPE", "lineman safety gear", "power line worker safety"
- Pexels/Unsplash: "construction worker safety equipment"

### 2.5 Data Checklist

```
□ Construction-PPE đã download (auto khi train lần đầu)
□ Class mapping đã verify (5 classes đúng)
□ Train/Val/Test split: 70% / 20% / 10% (có sẵn trong dataset)
□ Demo test images chuẩn bị xong (20 ảnh)
□ SH17 download NẾU accuracy Sprint 1 < 80%
□ dataset.yaml đã tạo với 5 classes chuẩn

Folder structure:
data/
├── raw/construction-ppe/    ← Auto-download
├── raw/sh17/                ← Nếu cần Tier 2
├── processed/               ← Merged + class mapped
└── demo/                    ← 20 test images cho presentation
```

---

## PHẦN 3 — PROJECT SETUP

### Bước 1: Tạo project structure

**Action**: Copy từ `_project-template/` → `projects/safety-ppe-checker/`

```
projects/safety-ppe-checker/
├── project-context.md      ← Business context, goals, users
├── glossary.md             ← PPE, bounding box, confidence score...
├── backlog.md              ← Product backlog
└── docs/
    ├── 01_product_requirements/
    ├── 02_technical_specs/
    ├── 03_plans/            ← File này đang ở đây
    ├── 04_testing/
    └── 05_ai_agent/
```

---

## PHẦN 4 — PRODUCT DOCUMENTATION (Tuần 1, Ngày 1-3)

### Bước 2: Viết PRD

- **Skill**: `write_prd`
- **Output**: `docs/01_product_requirements/prd/PRD-safety-ppe-checker.md`

**Key content:**
- Problem statement (từ 1.2)
- Goals: Reduce PPE violation rate / Tạo audit trail / Giảm thời gian kiểm tra
- Non-Goals: Nhận diện người, mobile native, video stream
- Success Metrics:
  - Detection accuracy ≥ 85% trên test set
  - False negative (miss vi phạm) < 10%
  - Thời gian xử lý ảnh < 3 giây
  - Demo chạy ổn định trong buổi trình bày

---

### Bước 3: Viết Epics (3 Epics)

- **Skill**: `write_epic`

| Epic | ID | Module | Mô tả |
|------|----|--------|-------|
| CV Engine | EPIC-CV-001 | cv-engine | Core AI detection engine |
| Web Interface | EPIC-WEB-001 | web-interface | Upload, camera, results UI |
| Dashboard | EPIC-DSH-001 | dashboard | Lịch sử, thống kê, báo cáo |

**Output paths:**
```
docs/01_product_requirements/
├── cv-engine/EPIC-CV-001.md
├── web-interface/EPIC-WEB-001.md
└── dashboard/EPIC-DSH-001.md
```

---

### Bước 4: Viết User Stories

- **Skill**: `write_user_story`

#### EPIC-CV-001 — CV Engine (4 stories)

| ID | Story | Priority |
|----|-------|----------|
| US-CV-001 | Là công nhân, tôi muốn hệ thống detect mũ bảo hộ trong ảnh | Must Have |
| US-CV-002 | Là công nhân, tôi muốn detect áo phản quang trong ảnh | Must Have |
| US-CV-003 | Là hệ thống, tôi cần trả về pass/fail tổng thể + từng hạng mục | Must Have |
| US-CV-004 | Là công nhân, tôi muốn xem bounding box trực quan trên ảnh kết quả | Should Have |

#### EPIC-WEB-001 — Web Interface (5 stories)

| ID | Story | Priority |
|----|-------|----------|
| US-WEB-001 | Là công nhân, tôi muốn upload ảnh từ máy tính để kiểm tra | Must Have |
| US-WEB-002 | Là công nhân, tôi muốn chụp ảnh trực tiếp từ webcam | Should Have |
| US-WEB-003 | Là công nhân, tôi muốn xem kết quả rõ ràng: pass/fail + màu sắc | Must Have |
| US-WEB-004 | Là công nhân, tôi muốn xem chi tiết từng hạng mục bị thiếu | Must Have |
| US-WEB-005 | Là giám sát, tôi muốn trang kết quả dễ screenshot để lưu hồ sơ | Nice to Have |

#### EPIC-DSH-001 — Dashboard (3 stories)

| ID | Story | Priority |
|----|-------|----------|
| US-DSH-001 | Là giám sát, tôi muốn xem danh sách lịch sử kiểm tra theo thời gian | Must Have |
| US-DSH-002 | Là giám sát, tôi muốn xem thống kê: tổng pass/fail, vi phạm nhiều nhất | Should Have |
| US-DSH-003 | Là giám sát, tôi muốn export báo cáo CSV đơn giản | Nice to Have |

---

## PHẦN 5 — TECHNICAL DESIGN (Tuần 1, Ngày 3-5)

### Bước 5: Architecture

- **Output**: `docs/02_technical_specs/architecture.md`

```
ARCHITECTURE OVERVIEW:

┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                       │
│  Upload/Camera → Preview → API Call → Results Display        │
│  Dashboard: History list + Chart (Chart.js)                   │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTP REST
┌─────────────────────────▼────────────────────────────────────┐
│                    BACKEND (FastAPI / Python)                  │
│  POST /api/v1/check-ppe  → CV Engine → Response              │
│  GET  /api/v1/history    → DB Query  → Response              │
│  GET  /api/v1/stats      → Aggregation → Response            │
└──────────────┬──────────────────────┬────────────────────────┘
               │                      │
┌──────────────▼───────┐   ┌──────────▼────────────────────┐
│   CV ENGINE          │   │   DATABASE (SQLite → Postgres) │
│   YOLOv8n model      │   │   Table: inspections           │
│   Preprocessing      │   │   - id, timestamp, image_path  │
│   Post-processing    │   │   - results_json, overall_pass │
│   Annotated image    │   └────────────────────────────────┘
└──────────────────────┘
```

**Tech Stack:**

| Layer | Technology | Lý do |
|-------|-----------|-------|
| Backend | FastAPI (Python) | ML-friendly, async, auto docs |
| CV Model | YOLOv8n (Ultralytics) | Nhanh, nhẹ, pretrained PPE có sẵn |
| Dataset | Roboflow PPE Dataset | Public, YOLOv8 format ready |
| Frontend | React + Tailwind CSS | Clean, responsive |
| DB | SQLite (dev) → PostgreSQL | Simple start, easy upgrade |
| Deployment | Docker Compose | 1 lệnh là chạy |

---

### Bước 6: Tech Specs (3 TPs)

**Output files:**
```
docs/02_technical_specs/
├── architecture.md
├── cv-engine/TP-CV-001.md        ← PPE Detection API spec
├── web-interface/TP-WEB-001.md   ← Frontend + Upload/Camera spec
└── dashboard/TP-DSH-001.md       ← History + Stats API spec
```

**TP-CV-001 — API Contract:**

```json
POST /api/v1/check-ppe
Input:  image (file, JPEG/PNG, max 10MB)

Output:
{
  "overall_pass": false,
  "confidence": 0.87,
  "processing_time_ms": 1240,
  "inspection_id": "uuid",
  "annotated_image_url": "/results/abc123.jpg",
  "items": {
    "helmet":          { "detected": true,  "confidence": 0.94 },
    "reflective_vest": { "detected": true,  "confidence": 0.89 },
    "gloves":          { "detected": false, "confidence": 0.0  },
    "safety_boots":    { "detected": true,  "confidence": 0.76 },
    "safety_glasses":  { "detected": false, "confidence": 0.0  }
  }
}
```

---

## PHẦN 6 — BUILD PLAN (Tuần 2-4)

### Sprint 1: Core Backend + CV Engine (22–28/03/2026)

**Goal**: API hoạt động, detect PPE từ ảnh

| Task | Chi tiết |
|------|---------|
| S1-01 | Setup FastAPI + Docker + folder structure |
| S1-02 | Load và verify dataset (từ Phần 2) |
| S1-03 | Fine-tune YOLOv8n hoặc dùng pretrained |
| S1-04 | Viết CV Engine: inference + post-processing |
| S1-05 | Implement POST /api/v1/check-ppe |
| S1-06 | DB model + save inspection |
| S1-07 | Test API với Postman, validate accuracy |
| S1-08 | Annotated image output với bounding boxes |

**Definition of Done:**
- [ ] API nhận ảnh → JSON với 5 PPE items pass/fail
- [ ] Accuracy ≥ 80% trên 20 test images
- [ ] Annotated image lưu và accessible
- [ ] Inspection lưu vào DB

**Rủi ro:**
- Pretrained không đủ tốt → dùng Construction PPE dataset, class mapping thủ công
- Gloves/glasses hay bị miss → hạ confidence threshold xuống 0.4

---

### Sprint 2: Frontend Web Interface (29/03–04/04/2026)

**Goal**: Demo UI hoàn chỉnh

| Task | Chi tiết |
|------|---------|
| S2-01 | Setup React + Tailwind + routing |
| S2-02 | Upload page: drag-drop + file picker + preview |
| S2-03 | Camera page: webcam capture (react-webcam) |
| S2-04 | Results page: annotated image + pass/fail cards |
| S2-05 | PPE Checklist: 5 items với icon + status màu |
| S2-06 | Overall verdict: GREEN (PASS) / RED (FAIL) |
| S2-07 | Loading state + error handling |
| S2-08 | Responsive layout (desktop + tablet) |

**UI Flow:**
```
Home
 ├── [Upload ảnh] ──→ Loading ──→ Results Page
 └── [Chụp webcam] ─→ Loading ──→ Results Page

Results Page:
┌──────────────────────────────────────────┐
│  ✅ PASS — ĐỦ TRANG BỊ BẢO HỘ          │
│  (hoặc ❌ FAIL — THIẾU TRANG BỊ)        │
├───────────────────┬──────────────────────┤
│  Ảnh kết quả      │  Checklist:          │
│  (bounding boxes) │  ✅ Mũ bảo hộ       │
│                   │  ✅ Áo phản quang   │
│                   │  ❌ Găng tay         │
│                   │  ✅ Giày bảo hộ     │
│                   │  ❌ Kính bảo hộ     │
├───────────────────┴──────────────────────┤
│  [Kiểm tra lại]  [Xem lịch sử]          │
└──────────────────────────────────────────┘
```

**Definition of Done:**
- [ ] Upload ảnh → kết quả hiển thị trong < 5 giây
- [ ] Webcam capture hoạt động trên Chrome
- [ ] Pass/Fail hiển thị rõ ràng với màu sắc
- [ ] 5 PPE items đúng status
- [ ] Không crash khi upload ảnh sai format

---

### Sprint 3: Dashboard + Polish + Demo Prep (05–12/04/2026)

**Goal**: Dashboard + mọi thứ sẵn sàng present

| Task | Chi tiết |
|------|---------|
| S3-01 | Dashboard: danh sách lịch sử kiểm tra |
| S3-02 | Stats: tổng pass/fail, vi phạm breakdown |
| S3-03 | Chart: Bar chart vi phạm theo loại (Chart.js) |
| S3-04 | Seed demo data: 20-30 inspections giả lập |
| S3-05 | Export CSV cơ bản |
| S3-06 | End-to-end testing: 10 test cases |
| S3-07 | Performance tune: < 3s processing time |
| S3-08 | Docker Compose: 1 lệnh `docker-compose up` là chạy |
| S3-09 | Viết demo script (kịch bản trình bày 15 phút) |
| S3-10 | Chuẩn bị test images: 5 PASS + 5 FAIL scenarios |

**Dashboard Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  DASHBOARD — Lịch sử kiểm tra PPE                          │
├──────────┬──────────┬──────────┬──────────────────────────┤
│ Tổng lượt│  PASS    │  FAIL    │  Tỷ lệ tuân thủ          │
│   247    │  198(80%)│  49(20%) │  ████████░░  80%         │
├──────────┴──────────┴──────────┴──────────────────────────┤
│  Vi phạm nhiều nhất:                                        │
│  Găng tay 45% | Kính 32% | Giày 12% | ...                 │
├────────────────────────────────────────────────────────────┤
│  Lịch sử:  [Thời gian]  [Kết quả]  [Vi phạm]  [Actions]  │
│  15/03 09:23   FAIL    Găng tay, Kính           [Xem]     │
│  15/03 09:18   PASS    —                        [Xem]     │
└────────────────────────────────────────────────────────────┘
```

---

## PHẦN 7 — TESTING PLAN

- **Output**: `docs/04_testing/test-strategy.md`

| TC | Scenario | Expected |
|----|----------|----------|
| TC-001 | Ảnh đủ 5 PPE, ánh sáng tốt | PASS, all 5 detected |
| TC-002 | Ảnh thiếu mũ | FAIL, helmet = false |
| TC-003 | Ảnh thiếu găng tay | FAIL, gloves = false |
| TC-004 | Ảnh mờ/tối | Kết quả + low confidence warning |
| TC-005 | Upload file không phải ảnh | Error 400: Invalid file format |
| TC-006 | Ảnh > 10MB | Error 413: File too large |
| TC-007 | Ảnh 2 người | Detect người gần nhất / cả 2 |
| TC-008 | Webcam capture + check | Kết quả giống upload |
| TC-009 | Dashboard load 30 records | Load < 2 giây |
| TC-010 | Export CSV | File download đúng data |

---

## PHẦN 8 — DOCUMENT MAP TỔNG THỂ

```
projects/safety-ppe-checker/
├── project-context.md                              ← Bước 1
├── glossary.md                                     ← Bước 1
├── backlog.md                                      ← Bước 1
└── docs/
    ├── 01_product_requirements/
    │   ├── prd/
    │   │   └── PRD-safety-ppe-checker.md           ← Bước 2
    │   ├── cv-engine/
    │   │   ├── EPIC-CV-001.md                      ← Bước 3
    │   │   ├── US-CV-001.md  (helmet detect)       ← Bước 4
    │   │   ├── US-CV-002.md  (vest detect)
    │   │   ├── US-CV-003.md  (pass/fail logic)
    │   │   └── US-CV-004.md  (bounding box)
    │   ├── web-interface/
    │   │   ├── EPIC-WEB-001.md                     ← Bước 3
    │   │   ├── US-WEB-001.md (upload)              ← Bước 4
    │   │   ├── US-WEB-002.md (camera)
    │   │   ├── US-WEB-003.md (results display)
    │   │   ├── US-WEB-004.md (checklist detail)
    │   │   └── US-WEB-005.md (screenshot)
    │   └── dashboard/
    │       ├── EPIC-DSH-001.md                     ← Bước 3
    │       ├── US-DSH-001.md (history)             ← Bước 4
    │       ├── US-DSH-002.md (stats)
    │       └── US-DSH-003.md (export CSV)
    ├── 02_technical_specs/
    │   ├── architecture.md                         ← Bước 5
    │   ├── cv-engine/
    │   │   └── TP-CV-001.md                        ← Bước 6
    │   ├── web-interface/
    │   │   └── TP-WEB-001.md                       ← Bước 6
    │   └── dashboard/
    │       └── TP-DSH-001.md                       ← Bước 6
    ├── 03_plans/
    │   └── MASTER-PLAN.md                          ← File này
    └── 04_testing/
        ├── test-strategy.md
        └── test-cases/
            └── TC-demo.md
```

---

## PHẦN 9 — TIMELINE TỔNG QUAN

| Tuần | Ngày | Phase | Milestone |
|------|------|-------|-----------|
| **Tuần 1** | 15–21/03 | Setup + Docs + Data | Project setup, PRD, Epics, Stories, Tech Specs, Dataset download |
| **Tuần 2** | 22–28/03 | Sprint 1 — Backend | FastAPI + YOLOv8 API hoạt động |
| **Tuần 3** | 29/03–04/04 | Sprint 2 — Frontend | Web UI: Upload + Camera + Results |
| **Tuần 4** | 05–12/04 | Sprint 3 — Polish | Dashboard + Testing + Demo ready |

---

## PROGRESS TRACKER

### Documentation (Tuần 1) ✅ COMPLETE
```
✅ project-context.md
✅ glossary.md
✅ backlog.md
✅ PRD-safety-ppe-checker.md
✅ EPIC-CV-001.md
✅ EPIC-WEB-001.md
✅ EPIC-DSH-001.md
✅ US-CV-001 to US-CV-004
✅ US-WEB-001 to US-WEB-005
✅ US-DSH-001 to US-DSH-003
✅ architecture.md
✅ TP-CV-001.md
✅ TP-WEB-001.md
✅ TP-DSH-001.md
✅ test-strategy.md (added 2026-03-15)
✅ TC-PPE-001.md test cases (added 2026-03-15)
✅ DATA-STRATEGY.md (added 2026-03-15)
✅ INSIGHTS-AND-TIPS.md (added 2026-03-15)
```

### Project Setup (Tuần 1) ✅ COMPLETE
```
✅ README.md
✅ .gitignore
✅ docker-compose.yml
✅ Backend folder structure (config, database, models, schemas, routers, services)
✅ requirements.txt
✅ Backend Dockerfile
✅ data/dataset.yaml (5 PPE classes)
✅ scripts/seed_demo_data.py
✅ PPE Guardrails skill created
```

### Data Preparation (Tuần 1 — song song)
```
□ Dataset downloaded từ Ultralytics (Construction-PPE)
✅ Class mapping verified (trong config.py + DATA-STRATEGY.md)
□ Train/Val/Test split done
□ 20 demo test images chuẩn bị xong
```

### Sprint 1 — Backend (Tuần 2)
```
✅ FastAPI project setup (main.py, config.py, database.py)
□ YOLOv8 model loaded & tested
□ POST /api/v1/check-ppe working (code ready, needs model)
□ Annotated image output
□ DB + inspection save
□ Accuracy ≥ 80% validated
```

### Sprint 2 — Frontend (Tuần 3)
```
□ React + Vite + Tailwind app setup
□ Upload page
□ Camera page
□ Results page
□ E2E flow working
```

### Sprint 3 — Polish (Tuần 4)
```
□ Dashboard page
□ Stats + Chart
□ Seed demo data (script ready: seed_demo_data.py)
□ Docker Compose working (config ready)
□ Demo script written
□ All test cases pass
```
