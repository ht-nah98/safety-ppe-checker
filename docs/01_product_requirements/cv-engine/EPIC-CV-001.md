# EPIC-CV-001: CV Engine — Lõi AI phát hiện PPE

> Core AI engine tự động detect 5 hạng mục PPE trong ảnh chụp toàn thân công nhân

---

## 1. Thông tin chung

| Mục | Nội dung |
|-----|----------|
| Epic ID | EPIC-CV-001 |
| Module | cv-engine |
| Version | v1.0 |
| Status | 📝 Draft |
| Priority | 🔴 Critical |
| Created | 2026-03-15 |

---

## 2. Tổng quan

### 2.1 Bối cảnh

Để hệ thống PPE Checker hoạt động, cần một lõi AI có khả năng nhận ảnh chụp toàn thân công nhân và phát hiện chính xác các trang bị bảo hộ đang được đeo. Đây là module cốt lõi mà toàn bộ hệ thống phụ thuộc vào.

**Pain Points hiện tại:**

| # | Pain Point | Mô tả |
|---|------------|-------|
| 1 | Kiểm tra thủ công | Giám sát phải nhìn mắt từng người, dễ bỏ sót |
| 2 | Không nhất quán | Tiêu chí "đủ PPE" phụ thuộc vào người kiểm tra |
| 3 | Không có bằng chứng | Không lưu được ảnh + kết quả kiểm tra |

### 2.2 Mục tiêu

Xây dựng API nhận ảnh đầu vào, chạy YOLOv8 inference, và trả về kết quả chi tiết pass/fail cho từng hạng mục PPE.

| # | Khả năng | Mô tả |
|---|----------|-------|
| 1 | Detect 5 PPE classes | helmet, reflective_vest, gloves, safety_boots, safety_glasses |
| 2 | Trả kết quả structured | JSON với pass/fail từng mục + overall_pass |
| 3 | Annotate ảnh | Vẽ bounding box + nhãn lên ảnh, trả URL |
| 4 | Lưu kết quả | Mỗi lần kiểm tra được lưu vào DB |

### 2.3 Business Value

| Giá trị | Mô tả | Metric |
|---------|-------|--------|
| Tự động hóa | Thay thế kiểm tra thủ công | Giảm thời gian từ ~30s → < 3s |
| Khách quan | AI không bị ảnh hưởng bởi cảm tính | Consistent across all checks |
| Audit trail | Mọi kết quả đều được lưu | 100% inspections logged |

### 2.4 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Detection accuracy (mAP@0.5) | ≥ 0.80 | Validate trên test set 50 ảnh |
| False negative rate | < 10% | Kiểm tra trên FAIL test images |
| Inference time | < 2 giây | Đo từ nhận ảnh → trả JSON |

---

## 3. Phạm vi

### 3.1 In-scope ✅

| # | Tính năng |
|---|-----------|
| 1 | API endpoint: POST /api/v1/check-ppe |
| 2 | YOLOv8n model inference cho 5 PPE classes |
| 3 | Post-processing: map detections → pass/fail checklist |
| 4 | Annotate ảnh với bounding boxes |
| 5 | Lưu inspection record vào DB |
| 6 | Trả về annotated image URL |

### 3.2 Out-of-scope ❌ (Phase 2)

| # | Tính năng | Lý do defer |
|---|-----------|-------------|
| 1 | Pose estimation | Tăng độ phức tạp, không cần cho demo |
| 2 | Detect "đội lệch mũ", "không cài dây" | Cần negative dataset riêng |
| 3 | Video stream / real-time | Cần infra khác |
| 4 | Multiple person detection | Chỉ cần detect 1 người trong demo |

---

## 4. Target Users

| User Role | Mô tả | Quyền |
|-----------|-------|-------|
| Công nhân | Gián tiếp — upload ảnh qua Web UI | Trigger inference |
| Hệ thống (Backend) | Gọi CV Engine và lấy kết quả | Full |

---

## 5. User Stories

| Story ID | Tên | Priority | Points | Status |
|----------|-----|----------|--------|--------|
| [US-CV-001](./US-CV-001.md) | Detect mũ bảo hộ trong ảnh | Must Have | 3 | ⬜ Todo |
| [US-CV-002](./US-CV-002.md) | Detect áo phản quang trong ảnh | Must Have | 2 | ⬜ Todo |
| [US-CV-003](./US-CV-003.md) | Trả về pass/fail tổng thể + từng hạng mục | Must Have | 3 | ⬜ Todo |
| [US-CV-004](./US-CV-004.md) | Bounding box trực quan trên ảnh kết quả | Should Have | 2 | ⬜ Todo |

**Total Story Points**: 10

---

## 6. Dependencies

### 6.1 Phụ thuộc vào
- Dataset: Roboflow PPE dataset đã download và processed (xem MASTER-PLAN Phần 2)
- Model: YOLOv8n pretrained hoặc fine-tuned

### 6.2 Blocks (các module phụ thuộc vào Epic này)
- EPIC-WEB-001: Web Interface gọi CV Engine API
- EPIC-DSH-001: Dashboard đọc inspection records từ DB do CV Engine tạo

---

## 7. Definition of Done

- [ ] Tất cả 4 User Stories đạt status "Done"
- [ ] API trả kết quả đúng cho cả 5 PPE classes
- [ ] mAP@0.5 ≥ 0.80 trên test set
- [ ] False negative < 10% trên FAIL images
- [ ] Annotated image được tạo và accessible
- [ ] Mỗi inspection được lưu vào DB

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Dataset thiếu class gloves/glasses | High | High | Dùng nhiều dataset nguồn, data augmentation |
| Accuracy thấp trên ảnh tối | Medium | Medium | Chuẩn bị demo images chất lượng tốt |
| Pretrained không fit PPE Việt Nam | Medium | Medium | Fine-tune hoặc class mapping từ construction dataset |

---

## 9. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial Epic Spec |

---

## Related Documents

- [PRD](../prd/PRD-safety-ppe-checker.md)
- [TP-CV-001](../../02_technical_specs/cv-engine/TP-CV-001.md)
- [Glossary](../../../glossary.md)
- [Master Plan — Data Section](../../03_plans/MASTER-PLAN.md#phần-2--sample-data--nguồn-dữ-liệu)
