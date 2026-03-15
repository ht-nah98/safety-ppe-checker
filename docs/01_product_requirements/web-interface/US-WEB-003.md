# US-WEB-003: Xem kết quả kiểm tra PPE rõ ràng với pass/fail và màu sắc

> Trang kết quả hiển thị verdict PASS/FAIL nổi bật và ảnh annotated

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-WEB-003 |
| Epic | [EPIC-WEB-001](./EPIC-WEB-001.md) - Web Interface |
| Priority | 🔴 Must Have |
| Story Points | 2 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** công nhân vừa kiểm tra PPE
**I want to** thấy kết quả ngay lập tức với màu sắc rõ ràng (xanh/đỏ)
**So that** tôi biết ngay mình pass hay fail mà không cần đọc chi tiết

---

## Bối cảnh

- Trang kết quả là điểm quan trọng nhất trong UX — phải rõ ràng trong < 1 giây nhìn
- Công nhân có thể không đọc kỹ — màu sắc phải đủ mạnh để truyền đạt thông điệp
- PASS = toàn bộ xanh lá, chữ to, icon ✅
- FAIL = đỏ, chữ to, icon ❌, rõ ràng là có vấn đề cần giải quyết

---

## Acceptance Criteria

### AC1: Verdict PASS hiển thị
**Given** API trả về `overall_pass = true`
**When** trang Results load
**Then** header hiển thị: "✅ PASS — ĐỦ TRANG BỊ BẢO HỘ" màu xanh lá (#00C851)
**And** nền header xanh lá nhạt
**And** ảnh annotated hiển thị bên trái

### AC2: Verdict FAIL hiển thị
**Given** API trả về `overall_pass = false`
**When** trang Results load
**Then** header hiển thị: "❌ FAIL — THIẾU TRANG BỊ BẢO HỘ" màu đỏ (#FF3547)
**And** nền header đỏ nhạt
**And** ảnh annotated hiển thị

### AC3: Ảnh annotated hiển thị đúng
**Given** `annotated_image_url` trong response
**When** trang load
**Then** ảnh annotated hiển thị với kích thước hợp lý (tối đa 50% width)
**And** ảnh có thể zoom khi click

### AC4: Navigation buttons
**Given** kết quả đã hiển thị
**When** nhìn xuống cuối trang
**Then** có 2 nút: "Kiểm tra lại" và "Xem lịch sử"
**And** "Kiểm tra lại" → về trang Home
**And** "Xem lịch sử" → sang Dashboard

---

## UI/UX Notes

```
┌──────────────────────────────────────────────┐
│  ✅ PASS — ĐỦ TRANG BỊ BẢO HỘ              │  ← Header to, full width
│  (nền xanh lá nhạt)                          │
├───────────────────────┬──────────────────────┤
│  [Ảnh annotated]      │  [Checklist - US-004] │  ← 2 cột
│                       │                      │
└───────────────────────┴──────────────────────┘
│  [Kiểm tra lại]   [Xem lịch sử]             │  ← Buttons
└──────────────────────────────────────────────┘
```

- Font verdict: 24–28px, bold
- Mobile: 2 cột chuyển thành 1 cột (ảnh trên, checklist dưới)

---

## Technical Notes

- Route: `/results/:inspectionId`
- Lấy data: GET `/api/v1/inspections/:inspectionId` hoặc pass qua state
- Hiển thị thời gian xử lý: "Đã phân tích trong X giây" (nhỏ, dưới verdict)

---

## Dependencies

- [ ] **Depends on**: US-CV-003 (response schema), US-CV-004 (annotated image URL)
- [ ] **Blocks**: US-WEB-004 (cùng trang)

---

## Definition of Done

- [ ] PASS/FAIL verdict hiển thị đúng màu sắc
- [ ] Ảnh annotated hiển thị
- [ ] Navigation buttons hoạt động
- [ ] Responsive trên desktop và tablet
- [ ] Test AC1–AC4 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
