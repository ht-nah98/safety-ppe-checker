# US-WEB-004: Xem chi tiết từng hạng mục PPE bị thiếu

> Checklist 5 PPE items với trạng thái từng mục, giúp công nhân biết cần bổ sung gì

---

## Thông tin

| Mục | Nội dung |
|-----|----------|
| Story ID | US-WEB-004 |
| Epic | [EPIC-WEB-001](./EPIC-WEB-001.md) - Web Interface |
| Priority | 🔴 Must Have |
| Story Points | 2 |
| Status | ⬜ To Do |

---

## User Story Statement

**As a** công nhân nhận kết quả FAIL
**I want to** thấy cụ thể tôi đang thiếu hạng mục PPE nào
**So that** tôi biết chính xác cần đi lấy thêm gì trước khi bắt đầu làm việc

---

## Bối cảnh

- Checklist hiển thị song song với ảnh annotated trên Results page
- 5 items theo thứ tự: Mũ bảo hộ, Áo phản quang, Găng tay, Giày bảo hộ, Kính bảo hộ
- Mỗi item có icon + tên tiếng Việt + trạng thái ✅/❌ + confidence score
- Khi FAIL: highlight rõ các items bị thiếu (đỏ, bold)

---

## Acceptance Criteria

### AC1: Hiển thị đủ 5 PPE items
**Given** kết quả từ API
**When** trang Results load
**Then** hiển thị đúng 5 rows: Mũ bảo hộ, Áo phản quang, Găng tay, Giày bảo hộ, Kính bảo hộ
**And** mỗi row có icon PPE tương ứng

### AC2: Item detected = ✅ xanh lá
**Given** `items.helmet.detected = true`
**When** render checklist
**Then** row "Mũ bảo hộ" hiển thị: ✅ icon xanh lá + "Mũ bảo hộ" + "94%"

### AC3: Item not detected = ❌ đỏ
**Given** `items.gloves.detected = false`
**When** render checklist
**Then** row "Găng tay" hiển thị: ❌ icon đỏ + "Găng tay" (bold, đỏ) + "Không phát hiện"

### AC4: Summary count
**Given** FAIL với 2 items thiếu
**When** trang load
**Then** dưới checklist có text: "Thiếu 2 hạng mục: Găng tay, Kính bảo hộ"

---

## UI/UX Notes

```
Checklist component:
┌─────────────────────────────────────────┐
│  ✅  🪖  Mũ bảo hộ            94%      │
│  ✅  🦺  Áo phản quang         89%      │
│  ❌  🧤  Găng tay        Không phát hiện│  ← đỏ, bold
│  ✅  👟  Giày bảo hộ          76%      │
│  ❌  🥽  Kính bảo hộ   Không phát hiện │  ← đỏ, bold
├─────────────────────────────────────────┤
│  ⚠️  Thiếu 2 hạng mục: Găng tay, Kính  │
└─────────────────────────────────────────┘
```

---

## Technical Notes

- Component: `<PPEChecklist items={inspectionResult.items} />`
- Map class names → tiếng Việt:
  ```
  helmet           → Mũ bảo hộ
  reflective_vest  → Áo phản quang
  gloves           → Găng tay
  safety_boots     → Giày bảo hộ
  safety_glasses   → Kính bảo hộ
  ```

---

## Dependencies

- [ ] **Depends on**: US-WEB-003 (cùng Results page)
- [ ] **Blocks**: Không có

---

## Definition of Done

- [ ] 5 items hiển thị đúng
- [ ] Màu sắc ✅/❌ đúng
- [ ] Confidence score hiển thị đúng
- [ ] Summary count đúng
- [ ] Test AC1–AC4 pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial story |
