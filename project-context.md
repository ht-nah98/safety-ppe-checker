# Project Context: Safety PPE Checker

> File này chứa bối cảnh quan trọng nhất của dự án. AI sẽ đọc file này ĐẦU TIÊN khi làm việc với project.

---

## 1. Overview

### Tên dự án
**Safety PPE Checker** — Hệ thống tự động đánh giá tuân thủ trang phục bảo hộ (PPE) qua ảnh chụp

### Mô tả ngắn gọn
Hệ thống sử dụng AI (YOLOv8) để phân tích ảnh chụp toàn thân công nhân điện lực, tự động kiểm tra 5 hạng mục trang bị bảo hộ cá nhân (PPE), và trả về kết quả pass/fail ngay lập tức. Mục tiêu của demo là chứng minh tính khả thi của giải pháp cho các doanh nghiệp điện lực.

### Problem Statement
Nhân viên điện lực (công nhân + giám sát) cần một cách để xác nhận đầy đủ trang bị PPE trước khi bắt đầu công việc, vì vi phạm PPE là nguyên nhân hàng đầu gây tai nạn lao động ngành điện. Hiện tại, giám sát viên phải kiểm tra thủ công từng người, gây tốn thời gian, dễ bỏ sót, và không có audit trail.

---

## 2. Business Context

### Business Goals
1. Chứng minh khả năng kỹ thuật AI detect PPE với độ chính xác ≥ 85%
2. Demo toàn bộ luồng: chụp ảnh → AI phân tích → kết quả → lưu lịch sử
3. Tạo nền tảng để pitch giải pháp cho công ty điện lực thực tế

### Success Metrics
| Metric | Target | How to Measure |
|--------|--------|----------------|
| Detection accuracy | ≥ 85% | Kiểm tra trên 50 test images |
| False negative rate (miss vi phạm) | < 10% | Đếm trên FAIL test images |
| Thời gian xử lý ảnh | < 3 giây | Đo từ upload → kết quả |
| Demo stability | 0 crash trong 30 phút demo | Manual testing |

### Stakeholders
| Role | Mô tả |
|------|-------|
| Builder / PO | Người xây dựng demo (bạn) |
| Target audience | Doanh nghiệp điện lực, bộ phận An toàn lao động |
| Evaluator | Giáo viên / chuyên gia đánh giá đề tài |

---

## 3. Users

### Primary Users
| User Type | Mô tả | Key Needs |
|-----------|-------|-----------|
| Công nhân điện lực | Người trực tiếp thực hiện công việc sửa chữa/bảo trì | Kiểm tra nhanh trước ca làm việc, biết mình thiếu gì |
| Giám sát an toàn | Quản lý tuân thủ PPE của đội | Xem lịch sử, thống kê vi phạm, xuất báo cáo |

### User Personas
- **Anh Minh** (công nhân): 35 tuổi, sửa chữa đường dây điện, cần kiểm tra PPE nhanh ≤ 30 giây mỗi sáng
- **Chị Lan** (giám sát): 42 tuổi, quản lý 20 công nhân, cần báo cáo tuân thủ hàng tuần

---

## 4. Product Scope

### In Scope (Demo)
- Upload ảnh hoặc chụp từ webcam
- AI detect 5 hạng mục PPE: mũ bảo hộ, áo phản quang, găng tay, giày bảo hộ, kính bảo hộ
- Hiển thị ảnh kết quả với bounding box + pass/fail từng mục
- Lưu lịch sử kiểm tra
- Dashboard: thống kê pass/fail + vi phạm theo loại PPE
- Export CSV cơ bản

### Out of Scope (Phase 2 — sau demo)
- Pose estimation (verify PPE đúng vị trí trên người)
- Nhận diện danh tính nhân viên (face recognition)
- Tích hợp hệ thống HR / chấm công
- Mobile app native (iOS/Android)
- Multi-job-type checklist (checklist khác theo loại công việc)
- Real-time video stream

### Constraints
- Timeline: 4 tuần (2026-03-15 → 2026-04-12)
- Dataset: chỉ dùng public dataset, chưa có dữ liệu thực từ công ty
- Deployment: local hoặc simple cloud, chưa cần production-grade

---

## 5. Technical Context

### Tech Stack
- Frontend: React + Tailwind CSS
- Backend: Python FastAPI
- CV Model: YOLOv8n (Ultralytics)
- Database: SQLite (dev) → PostgreSQL (prod)
- Deployment: Docker Compose

### Data Sources
- Primary dataset: Roboflow Universe — PPE Detection dataset
- Supplement: Construction PPE / Hard Hat Workers dataset
- Demo test images: 20 ảnh chuẩn bị sẵn (5 PASS + 15 FAIL scenarios)

### Integrations
- Roboflow API (download dataset)
- Ultralytics YOLOv8 (inference)

---

## 6. Timeline

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Project setup + Documentation | 2026-03-21 | ⬜ Planned |
| Sprint 1: Backend + CV Engine | 2026-03-28 | ⬜ Planned |
| Sprint 2: Frontend Web UI | 2026-04-04 | ⬜ Planned |
| Sprint 3: Dashboard + Demo Prep | 2026-04-12 | ⬜ Planned |

---

## 7. Key Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-15 | Dùng YOLOv8n thay vì YOLOv8m/l | Demo cần nhanh, nano đủ accuracy cho proof-of-concept |
| 2026-03-15 | Không làm pose estimation trong demo | Tăng phức tạp, không cần thiết cho proof-of-concept |
| 2026-03-15 | SQLite cho dev, PostgreSQL design cho prod | Đơn giản hóa setup ban đầu |
| 2026-03-15 | React + Tailwind cho frontend | Nhanh, clean, component-based |

---

## 8. Related Documents

| Document | Path | Mô tả |
|----------|------|-------|
| Master Plan | [MASTER-PLAN.md](./docs/03_plans/MASTER-PLAN.md) | Kế hoạch tổng thể 4 tuần |
| PRD | [PRD-safety-ppe-checker.md](./docs/01_product_requirements/prd/PRD-safety-ppe-checker.md) | Product Requirements |
| Architecture | [architecture.md](./docs/02_technical_specs/architecture.md) | Kiến trúc hệ thống |
| Backlog | [backlog.md](./backlog.md) | Product backlog |
