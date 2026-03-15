# US-CV-004: Bounding box trực quan trên ảnh kết quả

> Hệ thống xuất ảnh đã annotate với bounding box và nhãn cho từng PPE item detected

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-CV-004 |
| Epic | [EPIC-CV-001](./EPIC-CV-001.md) - CV Engine |
| Priority | 🟠 Should Have |
| Story Points | 2 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** công nhân xem kết quả
**I want to** thấy ảnh của mình với các ô vuông (bounding box) đánh dấu từng PPE được phát hiện
**So that** tôi hiểu trực quan AI đang phát hiện gì trên ảnh của mình

---

## Bối cảnh

- Annotated image là bằng chứng trực quan mạnh nhất để thuyết phục stakeholder
- Bounding box giúp công nhân hiểu tại sao kết quả PASS hoặc FAIL
- Ảnh annotated được lưu server-side và trả về URL để frontend display

---

## Acceptance Criteria

### AC1: Bounding box cho PPE detected
**Given** model detect được helmet với confidence ≥ threshold
**When** hệ thống annotate ảnh
**Then** ảnh xuất ra có bounding box màu xanh lá quanh mũ bảo hộ
**And** có nhãn text: "helmet 0.94" (class name + confidence)

### AC2: Màu sắc bounding box theo trạng thái
**Given** các PPE items được detect
**When** vẽ bounding boxes
**Then** dùng màu xanh lá (#00C851) cho tất cả detected items
**And** không vẽ bounding box cho items không detected (không confuse người dùng)

### AC3: Ảnh annotated accessible qua URL
**Given** inference hoàn thành và ảnh đã annotate
**When** hệ thống lưu ảnh
**Then** ảnh được lưu tại `/static/results/{inspection_id}.jpg`
**And** URL được trả trong response field `annotated_image_url`
**And** frontend có thể GET ảnh này

### AC4: Ảnh gốc và ảnh annotated đều được lưu
**Given** inspection hoàn thành
**When** kiểm tra storage
**Then** cả ảnh gốc và ảnh annotated đều được lưu
**And** DB reference đúng path

---

## UI/UX Notes

- Hiển thị ảnh annotated chiếm ~50% màn hình Results page (bên trái)
- Checklist 5 items hiển thị bên phải
- Font nhãn trên bounding box: đủ lớn để đọc được (14–16px equivalent)

---

## Technical Notes

- Thư viện annotate: OpenCV (`cv2.rectangle`, `cv2.putText`) hoặc PIL
- Output format: JPEG, quality 85%
- Naming: `{inspection_id}_annotated.jpg`
- Storage path: `./static/results/`
- FastAPI serve static files: `app.mount("/static", StaticFiles(directory="static"))`

---

## Dependencies

- [ ] **Depends on**: US-CV-003 (inference pipeline hoàn chỉnh)
- [ ] **Blocks**: US-WEB-003 (frontend hiển thị ảnh annotated)

---

## Definition of Done

- [ ] Annotated image được tạo đúng
- [ ] Bounding boxes đúng màu sắc
- [ ] URL accessible từ frontend
- [ ] Cả ảnh gốc và annotated đều lưu được
- [ ] Test AC1–AC4 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
