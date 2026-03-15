# PRD: Safety PPE Checker — Hệ thống tự động đánh giá tuân thủ PPE

**Document Version**: 1.0
**Created Date**: 2026-03-15
**Status**: Draft
**Project**: safety-ppe-checker

---

## 1. Overview

### 1.1 Problem Statement

Trong ngành điện lực, tai nạn lao động do thiếu trang bị bảo hộ cá nhân (PPE) là một trong những nguyên nhân gây thương vong hàng đầu. Trước mỗi ca làm việc, công nhân phải đảm bảo đã mặc đầy đủ: mũ bảo hộ, áo phản quang, găng tay, giày bảo hộ, và kính bảo hộ.

**Vấn đề hiện tại:**
- Giám sát viên kiểm tra PPE thủ công — tốn thời gian, dễ bỏ sót
- Không có audit trail: không lưu được ai đã kiểm tra, kết quả ra sao
- Khi xảy ra tai nạn, không có bằng chứng tuân thủ/vi phạm
- Quy trình phụ thuộc hoàn toàn vào con người — dễ bị "đối phó"

### 1.2 Solution Summary

Xây dựng hệ thống web cho phép công nhân chụp ảnh toàn thân, AI tự động phân tích và đánh giá từng hạng mục PPE trong vòng < 3 giây. Kết quả được lưu tự động, tạo audit trail đầy đủ. Giám sát viên có dashboard theo dõi tình trạng tuân thủ của cả đội.

**Đây là demo** nhằm chứng minh tính khả thi kỹ thuật trước khi triển khai thực tế tại doanh nghiệp.

### 1.3 Success Metrics

| Metric | Baseline | Target | Cách đo |
|--------|----------|--------|---------|
| Detection accuracy | 0% (manual) | ≥ 85% | Test trên 50 ảnh labeled |
| False negative rate | — | < 10% | Đếm trên FAIL test images |
| Thời gian xử lý | ~30 giây (manual) | < 3 giây | Đo từ upload → kết quả |
| Demo stability | — | 0 crash / 30 phút | Manual stress test |

---

## 2. Goals & Non-Goals

### 2.1 Goals (In Scope — Demo)

1. **AI Detection**: Tự động detect 5 hạng mục PPE trong ảnh toàn thân
2. **Instant Feedback**: Trả về kết quả pass/fail từng mục trong < 3 giây
3. **Visual Output**: Hiển thị ảnh với bounding box và nhãn từng PPE item
4. **Audit Trail**: Lưu lịch sử mọi lượt kiểm tra (thời gian, ảnh, kết quả)
5. **Dashboard**: Thống kê tỷ lệ tuân thủ và vi phạm theo loại PPE

### 2.2 Non-Goals (Out of Scope — Phase 2)

1. Pose estimation (kiểm tra PPE đúng vị trí trên người — mũ đội thẳng, dây đeo cài)
2. Nhận diện danh tính nhân viên (face recognition)
3. Tích hợp hệ thống HR, chấm công, ERP
4. Mobile app native (iOS/Android)
5. Checklist PPE khác nhau theo loại công việc
6. Real-time video stream / camera IP

---

## 3. Users & Stakeholders

### 3.1 Target Users

| User Type | Mô tả | Pain Points | Key Needs |
|-----------|-------|-------------|-----------|
| Công nhân điện lực | Thực hiện sửa chữa/bảo trì đường dây, tủ điện | Kiểm tra PPE mất thời gian, không biết mình thiếu gì | Kiểm tra nhanh ≤ 30 giây, biết ngay kết quả |
| Giám sát an toàn | Quản lý tuân thủ PPE của đội 20–50 người | Không có dữ liệu, phụ thuộc kiểm tra mắt | Dashboard, báo cáo, audit trail |

### 3.2 Stakeholders

| Role | Involvement |
|------|-------------|
| Builder / PO | Xây dựng và trình bày demo |
| Evaluator (giáo viên/chuyên gia) | Đánh giá tính khả thi và chất lượng |
| Target company (điện lực) | Khách hàng tiềm năng sau demo |

---

## 4. User Stories Overview

### EPIC-CV-001: CV Engine
| ID | Story | Priority |
|----|-------|----------|
| US-CV-001 | Detect mũ bảo hộ trong ảnh | Must Have |
| US-CV-002 | Detect áo phản quang trong ảnh | Must Have |
| US-CV-003 | Trả về pass/fail tổng thể + từng hạng mục | Must Have |
| US-CV-004 | Bounding box trực quan trên ảnh kết quả | Should Have |

### EPIC-WEB-001: Web Interface
| ID | Story | Priority |
|----|-------|----------|
| US-WEB-001 | Upload ảnh từ máy tính | Must Have |
| US-WEB-002 | Chụp ảnh từ webcam | Should Have |
| US-WEB-003 | Xem kết quả pass/fail rõ ràng | Must Have |
| US-WEB-004 | Xem chi tiết từng hạng mục bị thiếu | Must Have |
| US-WEB-005 | Trang kết quả dễ screenshot | Nice to Have |

### EPIC-DSH-001: Dashboard
| ID | Story | Priority |
|----|-------|----------|
| US-DSH-001 | Lịch sử kiểm tra theo thời gian | Must Have |
| US-DSH-002 | Thống kê pass/fail + vi phạm nhiều nhất | Should Have |
| US-DSH-003 | Export CSV | Nice to Have |

---

## 5. Functional Requirements

### 5.1 CV Engine

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CV-001 | Nhận ảnh JPEG/PNG tối đa 10MB | Must |
| FR-CV-002 | Detect 5 class PPE: helmet, reflective_vest, gloves, safety_boots, safety_glasses | Must |
| FR-CV-003 | Trả về confidence score cho mỗi class | Must |
| FR-CV-004 | Xác định overall_pass = true chỉ khi đủ cả 5 class | Must |
| FR-CV-005 | Xuất ảnh đã annotate với bounding box | Should |
| FR-CV-006 | Xử lý trong < 3 giây trên CPU thông thường | Must |

### 5.2 Web Interface

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-WEB-001 | Upload ảnh bằng file picker hoặc drag-and-drop | Must |
| FR-WEB-002 | Preview ảnh trước khi submit | Must |
| FR-WEB-003 | Chụp ảnh từ webcam (browser API) | Should |
| FR-WEB-004 | Hiển thị ảnh kết quả với bounding boxes | Must |
| FR-WEB-005 | Hiển thị 5 PPE items với trạng thái ✅/❌ | Must |
| FR-WEB-006 | Màu sắc verdict: xanh lá (PASS), đỏ (FAIL) | Must |
| FR-WEB-007 | Loading indicator trong lúc AI xử lý | Must |
| FR-WEB-008 | Error message khi upload sai format/size | Must |

### 5.3 Dashboard

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DSH-001 | Hiển thị danh sách lịch sử kiểm tra, sort theo thời gian mới nhất | Must |
| FR-DSH-002 | Mỗi row: timestamp, overall result, danh sách PPE vi phạm | Must |
| FR-DSH-003 | Tổng số lượt kiểm tra, số PASS, số FAIL | Should |
| FR-DSH-004 | Biểu đồ vi phạm theo loại PPE (bar chart) | Should |
| FR-DSH-005 | Export CSV với các cột: timestamp, result, violated_items | Nice |

---

## 6. Non-Functional Requirements

| Category | Requirement | Target |
|----------|-------------|--------|
| Performance | Thời gian xử lý ảnh (inference + annotate) | < 3 giây |
| Performance | Load dashboard 30 records | < 2 giây |
| Accuracy | PPE detection mAP@0.5 | ≥ 0.80 |
| Accuracy | False negative rate | < 10% |
| Usability | Người dùng không cần training | Giao diện tự giải thích |
| Compatibility | Chạy trên Chrome/Firefox desktop | 100% |
| Portability | Deploy bằng Docker Compose | 1 lệnh `docker-compose up` |
| File Support | JPEG, PNG | Max 10MB |

---

## 7. UX/UI Guidelines

### 7.1 Key User Flow

```
[Trang chủ]
    │
    ├──→ [Upload ảnh] ──→ Preview ──→ [Kiểm tra ngay]
    │                                        │
    └──→ [Chụp webcam] ──→ Capture ──→ [Kiểm tra ngay]
                                             │
                                    [Loading: AI đang phân tích]
                                             │
                                    [Trang kết quả]
                                       ├── Verdict (PASS/FAIL)
                                       ├── Ảnh annotated
                                       ├── Checklist 5 items
                                       └── [Kiểm tra lại] [Xem lịch sử]
```

### 7.2 Design Principles

- **Rõ ràng ngay lập tức**: PASS = xanh lá, FAIL = đỏ — nhìn là biết
- **Mobile-friendly layout**: Công nhân có thể dùng tablet tại cổng ra vào
- **Tối giản**: Không menu phức tạp, chỉ 3 trang: Home / Results / Dashboard

---

## 8. Technical Considerations

### 8.1 Dependencies

- **Ultralytics YOLOv8**: Inference engine
- **Roboflow PPE Dataset**: Training/fine-tuning data
- **FastAPI**: Backend framework
- **React + Tailwind**: Frontend
- **SQLite/PostgreSQL**: Lưu inspection records

### 8.2 Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Dataset thiếu class (gloves, glasses) | High | High | Dùng nhiều dataset, augmentation, hạ threshold |
| Accuracy thấp trên ảnh tối/ngược sáng | High | Medium | Ghi chú limitation, chuẩn bị demo images tốt |
| Inference quá chậm trên CPU | Medium | Low | Dùng YOLOv8n (nano), optimize image size |
| Pretrained model không fit PPE ngành điện VN | Medium | Medium | Fine-tune hoặc class mapping từ construction dataset |

---

## 9. Timeline & Milestones

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Documentation Complete | 2026-03-21 | PRD, Epics, Stories, Tech Specs xong |
| Sprint 1 Complete | 2026-03-28 | Backend + CV API hoạt động |
| Sprint 2 Complete | 2026-04-04 | Frontend hoàn chỉnh |
| Demo Ready | 2026-04-12 | Dashboard + Polish + Demo script |

---

## 10. Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | Dataset nào tốt nhất cho 5 class PPE ngành điện VN? | Open — cần research Phần 2 của Master Plan |
| 2 | Confidence threshold mặc định bao nhiêu là phù hợp? | Open — xác định sau khi test model |
| 3 | Demo sẽ được trình bày theo format nào? (live demo / video?) | Open |
| 4 | Cần thêm class nào ngoài 5 class hiện tại? | Open — confirm sau khi có feedback |

---

## Appendix

### A. PPE Classes Chuẩn

| Class Name (code) | Tên tiếng Việt | Bắt buộc |
|-------------------|----------------|----------|
| `helmet` | Mũ bảo hộ | Có |
| `reflective_vest` | Áo phản quang | Có |
| `gloves` | Găng tay bảo hộ | Có |
| `safety_boots` | Giày bảo hộ | Có |
| `safety_glasses` | Kính bảo hộ | Có |

### B. References

- [Master Plan](../../03_plans/MASTER-PLAN.md)
- [Architecture](../../02_technical_specs/architecture.md)
- [Glossary](../../../glossary.md)

### C. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-15 | Initial draft |
