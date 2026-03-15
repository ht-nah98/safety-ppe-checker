# US-DSH-002: Xem thống kê tổng quan và vi phạm nhiều nhất

> Dashboard hiển thị summary cards và biểu đồ vi phạm theo loại PPE

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-DSH-002 |
| Epic | [EPIC-DSH-001](./EPIC-DSH-001.md) - Dashboard |
| Priority | 🟠 Should Have |
| Story Points | 3 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** giám sát an toàn
**I want to** thấy ngay tổng quan: bao nhiêu lượt kiểm tra, tỷ lệ pass/fail, loại PPE nào hay bị thiếu nhất
**So that** tôi có thể đưa ra quyết định cải thiện training và quy trình an toàn

---

## Acceptance Criteria

### AC1: Summary cards
**Given** có data inspections trong DB
**When** Dashboard load
**Then** hiển thị 4 cards: Tổng lượt / Số PASS / Số FAIL / Tỷ lệ tuân thủ (%)

### AC2: Tỷ lệ tuân thủ đúng
**Given** 247 tổng, 198 PASS
**When** tính tỷ lệ
**Then** hiển thị "80%" và progress bar tương ứng

### AC3: Biểu đồ vi phạm theo loại PPE
**Given** dữ liệu vi phạm
**When** hiển thị chart
**Then** bar chart dọc với 5 bars: helmet, reflective_vest, gloves, safety_boots, safety_glasses
**And** chiều cao bar tỷ lệ với số lượt vi phạm của class đó
**And** gloves và safety_glasses thường cao nhất

### AC4: Data chính xác
**Given** seed data đã biết trước
**When** xem stats
**Then** numbers khớp với dữ liệu trong DB

---

## UI/UX Notes

```
Summary row:
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Tổng lượt│  │  PASS    │  │  FAIL    │  │ Tỷ lệ tuân   │
│   247    │  │ 198 (80%)│  │ 49 (20%) │  │ thủ: 80%     │
│          │  │          │  │          │  │ ████████░░   │
└──────────┘  └──────────┘  └──────────┘  └──────────────┘

Vi phạm theo loại:
Mũ bảo hộ    ▓▓░░░░░░  12%
Áo phản quang ▓░░░░░░░   8%
Găng tay     ▓▓▓▓▓░░░  45%  ← cao nhất
Giày bảo hộ  ▓▓░░░░░░  15%
Kính bảo hộ  ▓▓▓▓░░░░  32%
```

---

## Technical Notes

- API: `GET /api/v1/stats`
- Response:
  ```json
  {
    "total": 247,
    "pass": 198,
    "fail": 49,
    "compliance_rate": 0.80,
    "violations_by_class": {
      "helmet": 12,
      "reflective_vest": 8,
      "gloves": 45,
      "safety_boots": 15,
      "safety_glasses": 32
    }
  }
  ```
- Chart library: Chart.js (react-chartjs-2)

---

## Dependencies

- [ ] **Depends on**: US-DSH-001 (history table cùng trang)
- [ ] **Blocks**: Không có

---

## Definition of Done

- [ ] 4 summary cards hiển thị đúng
- [ ] Tỷ lệ tuân thủ tính đúng
- [ ] Bar chart render đúng với dữ liệu thực
- [ ] Test AC1–AC4 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
