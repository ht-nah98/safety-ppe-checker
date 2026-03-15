# EPIC-WEB-001: Web Interface — Giao diện kiểm tra PPE

> Giao diện web cho phép công nhân upload/chụp ảnh và xem kết quả kiểm tra PPE ngay lập tức

---

## 1. Thông tin chung

| Mục | Nội dung |
|-----|----------|
| Epic ID | EPIC-WEB-001 |
| Module | web-interface |
| Version | v1.0 |
| Status | 📝 Draft |
| Priority | 🔴 Critical |
| Created | 2026-03-15 |

---

## 2. Tổng quan

### 2.1 Bối cảnh

CV Engine đã có API, nhưng công nhân cần một giao diện trực quan để sử dụng — không cần biết kỹ thuật. Giao diện phải đơn giản đến mức công nhân có thể dùng ngay mà không cần hướng dẫn.

**Pain Points hiện tại:**

| # | Pain Point | Mô tả |
|---|------------|-------|
| 1 | Không có điểm kiểm tra | Không có nơi để công nhân tự kiểm tra PPE |
| 2 | Kết quả không rõ ràng | Khi bị nhắc nhở, công nhân không biết thiếu mục nào cụ thể |

### 2.2 Mục tiêu

Tạo web app với 2 luồng (upload + webcam) và trang kết quả cực kỳ rõ ràng, công nhân nhìn vào là biết ngay mình pass hay fail và thiếu gì.

| # | Khả năng | Mô tả |
|---|----------|-------|
| 1 | Upload ảnh | Drag-drop hoặc file picker |
| 2 | Chụp webcam | Capture trực tiếp từ camera máy tính/tablet |
| 3 | Xem kết quả trực quan | PASS = xanh lá, FAIL = đỏ, checklist 5 mục |
| 4 | Xem ảnh annotated | Ảnh với bounding boxes hiển thị PPE detected |

### 2.3 Business Value

| Giá trị | Mô tả | Metric |
|---------|-------|--------|
| Self-service | Công nhân tự kiểm tra, không cần chờ giám sát | Giảm bottleneck |
| Instant clarity | Biết ngay thiếu gì, sửa ngay | 0 ambiguity |
| Demo-ready | UI đẹp → thuyết phục stakeholder | Impression tốt |

### 2.4 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Upload → kết quả | < 5 giây (end-to-end) | Đo từ click submit → kết quả hiển thị |
| Webcam capture | Hoạt động trên Chrome | Manual test |
| Giao diện tự giải thích | Không cần training | User test với người không biết trước |

---

## 3. Phạm vi

### 3.1 In-scope ✅

| # | Tính năng |
|---|-----------|
| 1 | Trang Home: chọn giữa Upload và Webcam |
| 2 | Upload page: file picker, drag-drop, preview |
| 3 | Camera page: webcam capture bằng browser |
| 4 | Results page: verdict (PASS/FAIL), ảnh annotated, checklist 5 items |
| 5 | Loading state trong lúc AI xử lý |
| 6 | Error handling: sai format, quá size, server lỗi |
| 7 | Responsive layout (desktop + tablet) |

### 3.2 Out-of-scope ❌ (Phase 2)

| # | Tính năng | Lý do defer |
|---|-----------|-------------|
| 1 | Mobile app native | Sau khi có feedback |
| 2 | Login / user authentication | Không cần cho demo |
| 3 | Multi-language (EN/VI) | Chỉ cần tiếng Việt cho demo |
| 4 | Print report | Nice-to-have, thấp priority |

---

## 4. Target Users

| User Role | Mô tả | Quyền |
|-----------|-------|-------|
| Công nhân | Upload/chụp ảnh, xem kết quả | Full |
| Giám sát | Xem kết quả, navigate sang Dashboard | Full |

---

## 5. User Stories

| Story ID | Tên | Priority | Points | Status |
|----------|-----|----------|--------|--------|
| [US-WEB-001](./US-WEB-001.md) | Upload ảnh từ máy tính | Must Have | 3 | ⬜ Todo |
| [US-WEB-002](./US-WEB-002.md) | Chụp ảnh từ webcam | Should Have | 3 | ⬜ Todo |
| [US-WEB-003](./US-WEB-003.md) | Xem kết quả pass/fail rõ ràng | Must Have | 2 | ⬜ Todo |
| [US-WEB-004](./US-WEB-004.md) | Xem chi tiết từng hạng mục bị thiếu | Must Have | 2 | ⬜ Todo |
| [US-WEB-005](./US-WEB-005.md) | Trang kết quả dễ screenshot | Nice to Have | 1 | ⬜ Todo |

**Total Story Points**: 11

---

## 6. Dependencies

### 6.1 Phụ thuộc vào
- EPIC-CV-001: CV Engine API phải hoạt động trước (POST /api/v1/check-ppe)

### 6.2 Blocks
- EPIC-DSH-001: Dashboard link từ Results page

---

## 7. Definition of Done

- [ ] Tất cả 5 User Stories đạt status "Done"
- [ ] Upload ảnh → kết quả trong < 5 giây
- [ ] Webcam capture hoạt động trên Chrome/Firefox
- [ ] PASS/FAIL hiển thị rõ ràng với màu sắc
- [ ] Checklist 5 items đúng status
- [ ] Error handling: sai format, quá size
- [ ] Không crash khi test 30 lần liên tiếp

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Webcam không hoạt động trên mọi browser | Medium | Low | Test kỹ Chrome/Firefox, document known limitations |
| Ảnh preview lag với file lớn | Low | Medium | Resize client-side trước khi upload |
| CORS issues giữa frontend và backend | Medium | Medium | Configure CORS trong FastAPI |

---

## 9. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial Epic Spec |

---

## Related Documents

- [PRD](../prd/PRD-safety-ppe-checker.md)
- [EPIC-CV-001](../cv-engine/EPIC-CV-001.md)
- [TP-WEB-001](../../02_technical_specs/web-interface/TP-WEB-001.md)
- [Glossary](../../../glossary.md)
