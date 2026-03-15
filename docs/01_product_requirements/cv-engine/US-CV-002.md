# US-CV-002: Detect các hạng mục PPE còn lại

> Hệ thống phát hiện áo phản quang, găng tay, giày bảo hộ, kính bảo hộ trong ảnh

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-CV-002 |
| Epic | [EPIC-CV-001](./EPIC-CV-001.md) - CV Engine |
| Priority | 🔴 Must Have |
| Story Points | 2 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** hệ thống PPE Checker
**I want to** phát hiện áo phản quang, găng tay, giày bảo hộ, và kính bảo hộ trong ảnh
**So that** hệ thống kiểm tra đầy đủ cả 5 hạng mục PPE

---

## Bối cảnh

- 4 class còn lại sau helmet: `reflective_vest`, `gloves`, `safety_boots`, `safety_glasses`
- `reflective_vest`: áo có vạch phản quang sáng, dễ detect nhất sau helmet
- `gloves` và `safety_glasses`: nhỏ trong ảnh, hay bị miss — cần lower threshold (0.4)
- `safety_boots`: ở phần chân, cần ảnh toàn thân (không crop mặt)
- Dataset công khai ít ảnh gloves/glasses → cần data augmentation hoặc nhiều nguồn

---

## Acceptance Criteria

### AC1: Detect áo phản quang
**Given** công nhân mặc áo phản quang rõ ràng
**When** API nhận ảnh
**Then** `items.reflective_vest.detected = true` với confidence ≥ 0.5

### AC2: Detect găng tay
**Given** công nhân đang đeo găng tay (visible trong ảnh)
**When** API nhận ảnh
**Then** `items.gloves.detected = true` với confidence ≥ 0.4

### AC3: Detect giày bảo hộ
**Given** ảnh toàn thân, thấy rõ chân công nhân mang giày bảo hộ
**When** API nhận ảnh
**Then** `items.safety_boots.detected = true` với confidence ≥ 0.5

### AC4: Detect kính bảo hộ
**Given** công nhân đang đeo kính bảo hộ
**When** API nhận ảnh
**Then** `items.safety_glasses.detected = true` với confidence ≥ 0.4

### AC5: Không detect vật thể không phải PPE
**Given** ảnh có vật thể tương tự nhưng không phải PPE (kính mắt thường, giày thường)
**When** API nhận ảnh
**Then** confidence thấp và `detected = false` (không false positive)

---

## Technical Notes

- Confidence thresholds per class:
  ```
  reflective_vest:  0.50
  gloves:           0.40  (nhỏ trong ảnh)
  safety_boots:     0.50
  safety_glasses:   0.40  (nhỏ trong ảnh)
  ```
- Nếu dataset thiếu class này → data augmentation: flip, brightness, rotation

---

## Dependencies

- [ ] **Depends on**: US-CV-001 (cùng model, cùng inference pipeline)
- [ ] **Blocks**: US-CV-003

---

## Definition of Done

- [ ] Cả 4 class được detect đúng trên test images
- [ ] Threshold per-class đã set và document
- [ ] False positive < 15% trên từng class
- [ ] Test AC1–AC5 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
