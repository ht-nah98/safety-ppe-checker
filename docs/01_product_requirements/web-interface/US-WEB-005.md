# US-WEB-005: Trang kết quả dễ screenshot để lưu hồ sơ

> Trang Results được thiết kế layout sạch, dễ screenshot và lưu làm bằng chứng

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-WEB-005 |
| Epic | [EPIC-WEB-001](./EPIC-WEB-001.md) - Web Interface |
| Priority | 🟡 Nice to Have |
| Story Points | 1 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** giám sát an toàn
**I want to** dễ dàng screenshot trang kết quả kiểm tra PPE
**So that** tôi có thể lưu vào hồ sơ an toàn lao động hoặc gửi cho quản lý

---

## Acceptance Criteria

### AC1: Layout gọn cho screenshot
**Given** trang Results đang hiển thị
**When** giám sát screenshot trang
**Then** screenshot chứa: timestamp, verdict, ảnh annotated, checklist 5 items

### AC2: Timestamp rõ ràng
**Given** kết quả kiểm tra
**When** hiển thị trang
**Then** có timestamp rõ ràng "15/03/2026 09:23:45" trên trang

### AC3: Button download ảnh kết quả (optional)
**Given** trang Results
**When** click "Tải ảnh kết quả"
**Then** download ảnh annotated về máy

---

## Definition of Done

- [ ] Timestamp hiển thị rõ trên trang
- [ ] Layout không bị cắt khi screenshot toàn màn hình
- [ ] Test AC1–AC2 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
