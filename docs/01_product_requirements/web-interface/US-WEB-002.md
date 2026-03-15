# US-WEB-002: Chụp ảnh trực tiếp từ webcam để kiểm tra PPE

> Công nhân chụp ảnh toàn thân từ camera máy tính/tablet tại điểm kiểm tra

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-WEB-002 |
| Epic | [EPIC-WEB-001](./EPIC-WEB-001.md) - Web Interface |
| Priority | 🟠 Should Have |
| Story Points | 3 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** công nhân tại điểm kiểm tra PPE
**I want to** chụp ảnh trực tiếp từ webcam mà không cần dùng điện thoại riêng
**So that** tôi có thể kiểm tra PPE ngay tại chỗ, nhanh hơn

---

## Bối cảnh

- Use case: máy tính/tablet được cài đặt tại cổng vào khu vực làm việc
- Dùng browser WebRTC API (`getUserMedia`)
- Chỉ cần hoạt động trên Chrome (phổ biến nhất trong môi trường doanh nghiệp)
- Công nhân đứng cách camera ~1–2 mét để toàn thân vào frame

---

## Acceptance Criteria

### AC1: Mở webcam thành công
**Given** người dùng click "Chụp webcam" trên trang Home
**When** browser yêu cầu quyền camera và người dùng cho phép
**Then** hiển thị live video feed từ camera
**And** có nút "Chụp ảnh" trên màn hình

### AC2: Chụp ảnh từ webcam
**Given** video feed đang hiển thị
**When** click "Chụp ảnh"
**Then** frame hiện tại được capture thành ảnh
**And** video dừng lại, hiển thị ảnh captured làm preview
**And** xuất hiện nút "Kiểm tra ngay" và "Chụp lại"

### AC3: Chụp lại
**Given** ảnh đã được capture nhưng muốn chụp lại
**When** click "Chụp lại"
**Then** video feed tiếp tục, có thể chụp ảnh mới

### AC4: Từ chối quyền camera
**Given** người dùng không cho phép browser truy cập camera
**When** browser request bị từ chối
**Then** hiển thị thông báo: "Cần cấp quyền camera — vui lòng kiểm tra cài đặt trình duyệt"
**And** có option để chuyển sang Upload ảnh thay thế

### AC5: Không có camera
**Given** thiết bị không có camera
**When** click "Chụp webcam"
**Then** hiển thị thông báo: "Không tìm thấy camera"
**And** gợi ý dùng Upload ảnh

---

## UI/UX Notes

- Trang camera: video feed full width, nút "Chụp ảnh" nổi bật ở dưới
- Guide overlay: khung hình người (silhouette) để công nhân biết đứng vị trí nào
- Countdown 3 giây trước khi chụp (optional, nice to have)
- Flip camera (mirror) để trải nghiệm tự nhiên hơn

---

## Technical Notes

- Thư viện: `react-webcam` hoặc native `getUserMedia` API
- Capture format: JPEG, quality 0.85
- Resolution tối thiểu: 640×480 (đủ cho YOLOv8 inference)
- Stop camera stream khi rời trang (cleanup)

---

## Dependencies

- [ ] **Depends on**: US-WEB-001 (upload flow phải xong trước làm reference)
- [ ] **Blocks**: Không có

---

## Definition of Done

- [ ] Webcam mở được trên Chrome
- [ ] Capture ảnh và preview hoạt động
- [ ] Chụp lại hoạt động
- [ ] Error state (từ chối quyền, không có camera) hoạt động
- [ ] Camera stream được stop khi rời trang
- [ ] Test AC1–AC5 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
