# US-CV-001: Detect mũ bảo hộ trong ảnh

> Hệ thống phát hiện có/không có mũ bảo hộ (helmet) trong ảnh chụp toàn thân công nhân

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-CV-001 |
| Epic | [EPIC-CV-001](./EPIC-CV-001.md) - CV Engine |
| Priority | 🔴 Must Have |
| Story Points | 3 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** hệ thống PPE Checker
**I want to** phát hiện mũ bảo hộ trong ảnh chụp toàn thân công nhân
**So that** hệ thống có thể xác định công nhân có đội mũ bảo hộ hay không

---

## Bối cảnh

- Đây là hạng mục PPE quan trọng nhất và phổ biến nhất trong dataset
- Confidence threshold mặc định: 0.5 — nếu score ≥ 0.5 thì coi là detected
- Mũ bảo hộ xuất hiện ở phần trên đầu người trong ảnh
- Dataset: class `helmet` hoặc `hardhat` cần được map về `helmet` trong hệ thống

---

## Acceptance Criteria

### AC1: Detect thành công mũ bảo hộ
**Given** công nhân đội mũ bảo hộ và chụp ảnh toàn thân rõ nét
**When** API POST /api/v1/check-ppe nhận ảnh
**Then** response trả về `items.helmet.detected = true`
**And** `items.helmet.confidence ≥ 0.5`

### AC2: Phát hiện không có mũ
**Given** công nhân không đội mũ bảo hộ
**When** API nhận ảnh
**Then** response trả về `items.helmet.detected = false`
**And** `items.helmet.confidence = 0.0`

### AC3: Ảnh mờ / ánh sáng kém
**Given** ảnh có chất lượng thấp nhưng vẫn nhìn thấy người
**When** API nhận ảnh
**Then** hệ thống vẫn trả về kết quả (không throw exception)
**And** confidence score thấp phản ánh độ tin cậy giảm

---

## UI/UX Notes

- Kết quả hiển thị trên Results page: "✅ Mũ bảo hộ" hoặc "❌ Mũ bảo hộ"
- Bounding box màu xanh lá (detected) hoặc không vẽ (not detected)

---

## Technical Notes

- Model class: `helmet` (sau class mapping từ các dataset ngoài)
- Confidence threshold: `HELMET_THRESHOLD = 0.5` (configurable)
- Inference engine: Ultralytics YOLOv8n

---

## Dependencies

- [ ] **Depends on**: Dataset đã download và processed
- [ ] **Blocks**: US-CV-003 (pass/fail tổng thể phụ thuộc vào tất cả 5 class)

---

## Definition of Done

- [ ] YOLOv8 detect đúng helmet trên ≥ 80% test images
- [ ] API trả về `items.helmet` đúng format
- [ ] Test AC1, AC2, AC3 đều pass
- [ ] Class mapping từ dataset ngoài đã verify

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
