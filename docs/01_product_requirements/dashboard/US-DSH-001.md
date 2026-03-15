# US-DSH-001: Xem danh sách lịch sử kiểm tra PPE theo thời gian

> Dashboard hiển thị toàn bộ lịch sử các lượt kiểm tra, mới nhất trước

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-DSH-001 |
| Epic | [EPIC-DSH-001](./EPIC-DSH-001.md) - Dashboard |
| Priority | 🔴 Must Have |
| Story Points | 3 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** giám sát an toàn
**I want to** xem danh sách tất cả lượt kiểm tra PPE sắp xếp theo thời gian mới nhất
**So that** tôi có thể theo dõi lịch sử và xác minh ai đã kiểm tra, kết quả ra sao

---

## Bối cảnh

- Dashboard là trang dành cho giám sát, không phải công nhân
- Cần seed 20–30 inspection records giả lập cho demo
- Mỗi row: timestamp, kết quả, danh sách vi phạm, link xem ảnh chi tiết
- Pagination hoặc scroll — 20 items per page là đủ cho demo

---

## Acceptance Criteria

### AC1: Danh sách lịch sử load thành công
**Given** có ít nhất 1 inspection trong DB
**When** giám sát truy cập trang Dashboard
**Then** danh sách hiển thị các inspections, sort mới nhất trước
**And** mỗi row có: timestamp, PASS/FAIL badge, danh sách item vi phạm

### AC2: PASS/FAIL badge rõ ràng
**Given** inspection với overall_pass = true
**When** hiển thị trong bảng
**Then** badge "PASS" màu xanh lá
**And** inspection với overall_pass = false → badge "FAIL" màu đỏ

### AC3: Xem chi tiết inspection
**Given** danh sách đang hiển thị
**When** click vào row hoặc nút "Xem"
**Then** navigate sang Results page của inspection đó

### AC4: Trạng thái không có data
**Given** DB không có inspection nào
**When** Dashboard load
**Then** hiển thị: "Chưa có lượt kiểm tra nào. Hãy bắt đầu kiểm tra!"

### AC5: Performance
**Given** có 30 inspection records
**When** Dashboard load
**Then** danh sách hiển thị trong < 2 giây

---

## UI/UX Notes

```
Bảng lịch sử:
┌──────────────────┬────────┬──────────────────────┬──────────┐
│  Thời gian       │ Kết quả│ Vi phạm              │ Actions  │
├──────────────────┼────────┼──────────────────────┼──────────┤
│ 15/03 09:23:45   │ FAIL   │ Găng tay, Kính       │ [Xem]    │
│ 15/03 09:18:12   │ PASS   │ —                    │ [Xem]    │
│ 15/03 08:55:30   │ FAIL   │ Giày bảo hộ          │ [Xem]    │
└──────────────────┴────────┴──────────────────────┴──────────┘
```

---

## Technical Notes

- API: `GET /api/v1/inspections?limit=20&offset=0`
- Response: `{ inspections: [...], total: N }`
- Seed data script: `scripts/seed_demo_data.py` tạo 30 inspections realistic

---

## Dependencies

- [ ] **Depends on**: US-CV-003 (inspections được tạo trong DB)
- [ ] **Blocks**: US-DSH-002

---

## Definition of Done

- [ ] Danh sách load đúng từ API
- [ ] Sort đúng (mới nhất trước)
- [ ] Badge PASS/FAIL đúng màu
- [ ] Link xem chi tiết hoạt động
- [ ] Seed data 30 records đã có
- [ ] Performance < 2 giây
- [ ] Test AC1–AC5 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
