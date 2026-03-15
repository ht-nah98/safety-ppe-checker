# US-CV-003: Trả về kết quả pass/fail tổng thể + từng hạng mục

> API trả về JSON chuẩn với overall_pass và chi tiết từng PPE item

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-CV-003 |
| Epic | [EPIC-CV-001](./EPIC-CV-001.md) - CV Engine |
| Priority | 🔴 Must Have |
| Story Points | 3 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** hệ thống PPE Checker
**I want to** nhận ảnh và trả về JSON kết quả đầy đủ bao gồm overall_pass và từng PPE item
**So that** Frontend có thể hiển thị kết quả rõ ràng và DB có thể lưu đầy đủ thông tin

---

## Bối cảnh

- `overall_pass = true` CHỈ KHI tất cả 5 class đều `detected = true`
- Thiếu bất kỳ 1 item nào → `overall_pass = false`
- Response phải nhất quán về schema bất kể kết quả detection ra sao
- Mỗi inspection phải được lưu vào DB với `inspection_id` duy nhất

---

## Acceptance Criteria

### AC1: PASS — đủ cả 5 PPE
**Given** ảnh công nhân có đủ helmet, reflective_vest, gloves, safety_boots, safety_glasses
**When** POST /api/v1/check-ppe nhận ảnh
**Then** response: `overall_pass = true`
**And** tất cả 5 items đều `detected = true`
**And** `inspection_id` là UUID hợp lệ
**And** inspection được lưu vào DB

### AC2: FAIL — thiếu ít nhất 1 item
**Given** ảnh công nhân thiếu ≥ 1 PPE item
**When** API nhận ảnh
**Then** `overall_pass = false`
**And** item bị thiếu có `detected = false`, `confidence = 0.0`
**And** inspection được lưu vào DB với `overall_pass = false`

### AC3: Response schema luôn nhất quán
**Given** bất kỳ ảnh hợp lệ nào
**When** API trả response
**Then** response luôn có đủ các field: `overall_pass`, `inspection_id`, `processing_time_ms`, `annotated_image_url`, `items` (5 class)
**And** không có field nào bị thiếu hay null

### AC4: Lỗi ảnh không hợp lệ
**Given** file không phải ảnh JPEG/PNG hoặc vượt 10MB
**When** API nhận file
**Then** trả HTTP 400 với message mô tả lỗi
**And** KHÔNG lưu vào DB

---

## Technical Notes

- API endpoint: `POST /api/v1/check-ppe`
- Response schema:
  ```json
  {
    "overall_pass": boolean,
    "inspection_id": "uuid-v4",
    "processing_time_ms": integer,
    "annotated_image_url": "string",
    "items": {
      "helmet":          { "detected": boolean, "confidence": float },
      "reflective_vest": { "detected": boolean, "confidence": float },
      "gloves":          { "detected": boolean, "confidence": float },
      "safety_boots":    { "detected": boolean, "confidence": float },
      "safety_glasses":  { "detected": boolean, "confidence": float }
    }
  }
  ```
- DB table: `inspections` — id, timestamp, overall_pass, results_json, image_path, annotated_image_path

---

## Dependencies

- [ ] **Depends on**: US-CV-001, US-CV-002 (detection pipeline hoàn chỉnh)
- [ ] **Blocks**: US-WEB-003, US-WEB-004 (frontend cần response schema này)

---

## Definition of Done

- [ ] API endpoint hoạt động end-to-end
- [ ] Schema validated bằng Pydantic model
- [ ] overall_pass logic đúng (AND của 5 class)
- [ ] Inspection lưu DB đầy đủ
- [ ] Test AC1–AC4 pass
- [ ] Postman collection test documented

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
