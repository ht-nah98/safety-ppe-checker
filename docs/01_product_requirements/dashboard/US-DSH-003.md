# US-DSH-003: Export báo cáo lịch sử kiểm tra dạng CSV

> Giám sát xuất toàn bộ lịch sử kiểm tra PPE ra file CSV

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-DSH-003 |
| Epic | [EPIC-DSH-001](./EPIC-DSH-001.md) - Dashboard |
| Priority | 🟡 Nice to Have |
| Story Points | 2 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** giám sát an toàn
**I want to** export lịch sử kiểm tra PPE ra file CSV
**So that** tôi có thể mở trong Excel và làm báo cáo cho quản lý

---

## Acceptance Criteria

### AC1: Download CSV thành công
**Given** có inspections trong DB
**When** click "Export CSV" trên Dashboard
**Then** file CSV được download về máy
**And** tên file: `ppe-inspections-{date}.csv`

### AC2: Cấu trúc CSV đúng
**Given** file CSV được download
**When** mở bằng Excel
**Then** có các cột: `Thời gian`, `Kết quả`, `Mũ bảo hộ`, `Áo phản quang`, `Găng tay`, `Giày bảo hộ`, `Kính bảo hộ`
**And** mỗi row là 1 inspection
**And** giá trị: "PASS"/"FAIL" cho kết quả, "Có"/"Không" cho từng PPE item

---

## Technical Notes

- API: `GET /api/v1/inspections/export?format=csv`
- Backend: dùng Python `csv` module hoặc pandas
- Encoding: UTF-8 with BOM (để Excel đọc được tiếng Việt)

---

## Definition of Done

- [ ] Download CSV hoạt động
- [ ] Encoding UTF-8 BOM đúng (tiếng Việt không bị lỗi font)
- [ ] Cấu trúc cột đúng
- [ ] Test AC1–AC2 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
