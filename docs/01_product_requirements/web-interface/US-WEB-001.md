# US-WEB-001: Upload ảnh từ máy tính để kiểm tra PPE

> Công nhân upload ảnh từ máy tính/tablet để AI kiểm tra PPE

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-WEB-001 |
| Epic | [EPIC-WEB-001](./EPIC-WEB-001.md) - Web Interface |
| Priority | 🔴 Must Have |
| Story Points | 3 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** công nhân điện lực
**I want to** upload ảnh toàn thân của mình từ máy tính
**So that** AI có thể kiểm tra tôi đã mặc đủ PPE chưa

---

## Bối cảnh

- Đây là luồng chính (primary flow) — upload trước, webcam là luồng phụ
- Hỗ trợ file JPEG và PNG, tối đa 10MB
- Preview ảnh trước khi submit để user confirm đúng ảnh
- Khi submit, gọi POST /api/v1/check-ppe và chuyển sang Results page

---

## Acceptance Criteria

### AC1: Upload ảnh thành công
**Given** người dùng ở trang Home
**When** click "Upload ảnh" và chọn file JPEG/PNG ≤ 10MB
**Then** ảnh hiển thị preview trên màn hình
**And** nút "Kiểm tra ngay" xuất hiện và clickable

### AC2: Submit kiểm tra
**Given** ảnh đã được preview
**When** click "Kiểm tra ngay"
**Then** hiển thị loading indicator "AI đang phân tích..."
**And** gọi API POST /api/v1/check-ppe với ảnh
**And** chuyển sang Results page khi có kết quả

### AC3: File sai định dạng
**Given** người dùng chọn file không phải JPEG/PNG (ví dụ: .pdf, .docx)
**When** file được chọn
**Then** hiển thị thông báo: "Chỉ hỗ trợ ảnh JPEG hoặc PNG"
**And** preview không hiển thị, nút submit không xuất hiện

### AC4: File quá lớn
**Given** người dùng chọn file ảnh > 10MB
**When** file được chọn
**Then** hiển thị thông báo: "Ảnh quá lớn — tối đa 10MB"
**And** không gọi API

### AC5: Drag and drop
**Given** người dùng drag một ảnh vào vùng upload
**When** thả file vào
**Then** file được load giống như chọn qua file picker

---

## UI/UX Notes

- Upload zone: hình chữ nhật dashed border, icon upload ở giữa, text "Kéo thả ảnh vào đây hoặc click để chọn"
- Preview: ảnh hiển thị dưới upload zone, có nút "Xóa" để chọn lại
- Button "Kiểm tra ngay": màu xanh dương, full-width, xuất hiện sau khi có preview
- Loading: spinner + text "AI đang phân tích... (~2-3 giây)"

---

## Technical Notes

- Input: `<input type="file" accept="image/jpeg,image/png">`
- Client-side validation: file type + size trước khi gọi API
- API call: `FormData` với field `image`
- Timeout: 30 giây (nếu quá thời gian → hiện lỗi kết nối)

---

## Dependencies

- [ ] **Depends on**: US-CV-003 (API endpoint sẵn sàng)
- [ ] **Blocks**: US-WEB-003, US-WEB-004 (Results page cần kết quả từ story này)

---

## Definition of Done

- [ ] Upload file picker hoạt động
- [ ] Drag-and-drop hoạt động
- [ ] Preview hiển thị đúng
- [ ] Validation sai format / quá size hoạt động
- [ ] Loading indicator hiển thị khi submit
- [ ] Navigate sang Results page sau khi có kết quả
- [ ] Test AC1–AC5 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
