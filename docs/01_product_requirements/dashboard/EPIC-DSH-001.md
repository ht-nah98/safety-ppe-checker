# EPIC-DSH-001: Dashboard — Quản lý & thống kê kiểm tra PPE

> Dashboard cho giám sát an toàn theo dõi lịch sử kiểm tra, tỷ lệ vi phạm, và xuất báo cáo

---

## 1. Thông tin chung

| Mục | Nội dung |
|-----|----------|
| Epic ID | EPIC-DSH-001 |
| Module | dashboard |
| Version | v1.0 |
| Status | 📝 Draft |
| Priority | 🟠 High |
| Created | 2026-03-15 |

---

## 2. Tổng quan

### 2.1 Bối cảnh

Sau khi công nhân kiểm tra PPE, giám sát an toàn cần một nơi tổng hợp dữ liệu — xem ai kiểm tra lúc nào, tỷ lệ vi phạm ra sao, loại PPE nào hay bị thiếu nhất. Đây cũng là phần quan trọng để thuyết phục stakeholder vì nó thể hiện giá trị dữ liệu của hệ thống.

**Pain Points hiện tại:**

| # | Pain Point | Mô tả |
|---|------------|-------|
| 1 | Không có dữ liệu lịch sử | Không biết tần suất vi phạm, loại vi phạm nào phổ biến |
| 2 | Báo cáo thủ công | Giám sát phải tự ghi chép, tốn thời gian, không đáng tin cậy |

### 2.2 Mục tiêu

Cung cấp dashboard đơn giản nhưng đủ thuyết phục, thể hiện rằng hệ thống tạo ra dữ liệu có giá trị cho quản lý an toàn lao động.

| # | Khả năng | Mô tả |
|---|----------|-------|
| 1 | Xem lịch sử | Danh sách toàn bộ lượt kiểm tra, sort mới nhất trước |
| 2 | Thống kê tổng quan | Tổng lượt, số PASS/FAIL, tỷ lệ tuân thủ |
| 3 | Phân tích vi phạm | Loại PPE nào bị vi phạm nhiều nhất |
| 4 | Export | Xuất CSV để dùng trong báo cáo |

### 2.3 Business Value

| Giá trị | Mô tả | Metric |
|---------|-------|--------|
| Insight | Biết ngay loại PPE nào hay bị thiếu → cải thiện training | % vi phạm theo loại |
| Accountability | Audit trail đầy đủ → trách nhiệm rõ ràng | 100% logged |
| ROI visibility | Thấy được số lượng vi phạm được phát hiện | Số vi phạm / ngày |

### 2.4 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dashboard load time | < 2 giây (30 records) | Measure |
| Dữ liệu seed demo | ≥ 30 inspections sẵn có | Manual check |
| Chart hiển thị đúng | 5 PPE classes, đúng count | Manual verify |

---

## 3. Phạm vi

### 3.1 In-scope ✅

| # | Tính năng |
|---|-----------|
| 1 | Summary cards: Tổng lượt / PASS / FAIL / Tỷ lệ tuân thủ |
| 2 | Bar chart: số vi phạm theo từng loại PPE |
| 3 | History table: timestamp, result, violated items, link xem chi tiết |
| 4 | Seed data: 20–30 inspections giả lập sẵn cho demo |
| 5 | Export CSV |

### 3.2 Out-of-scope ❌ (Phase 2)

| # | Tính năng | Lý do defer |
|---|-----------|-------------|
| 1 | Filter theo ngày / người / loại vi phạm | Thêm phức tạp |
| 2 | Trend chart theo thời gian | Cần nhiều data hơn |
| 3 | Email alerts | Cần email infra |
| 4 | User management | Không cần cho demo |

---

## 4. Target Users

| User Role | Mô tả | Quyền |
|-----------|-------|-------|
| Giám sát an toàn | Xem toàn bộ dashboard | Full |
| Công nhân | Có thể link đến từ Results page | View only |

---

## 5. User Stories

| Story ID | Tên | Priority | Points | Status |
|----------|-----|----------|--------|--------|
| [US-DSH-001](./US-DSH-001.md) | Xem lịch sử kiểm tra theo thời gian | Must Have | 3 | ⬜ Todo |
| [US-DSH-002](./US-DSH-002.md) | Thống kê tổng quan + vi phạm nhiều nhất | Should Have | 3 | ⬜ Todo |
| [US-DSH-003](./US-DSH-003.md) | Export báo cáo CSV | Nice to Have | 2 | ⬜ Todo |

**Total Story Points**: 8

---

## 6. Dependencies

### 6.1 Phụ thuộc vào
- EPIC-CV-001: Inspection records được tạo bởi CV Engine
- EPIC-WEB-001: Navigation link từ Results page sang Dashboard

### 6.2 Blocks
- Không có — đây là module cuối

---

## 7. Definition of Done

- [ ] Tất cả 3 User Stories đạt status "Done"
- [ ] Dashboard load < 2 giây với 30 records
- [ ] Chart hiển thị đúng dữ liệu vi phạm
- [ ] Seed data 20–30 inspections đã được load
- [ ] Export CSV hoạt động đúng
- [ ] Navigation từ Results page hoạt động

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Không có đủ data thật để demo | Medium | High | Seed 30 inspections giả lập, realistic timestamps |
| Chart library không render đẹp | Low | Low | Dùng Chart.js — stable và đẹp |

---

## 9. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial Epic Spec |

---

## Related Documents

- [PRD](../prd/PRD-safety-ppe-checker.md)
- [EPIC-CV-001](../cv-engine/EPIC-CV-001.md)
- [TP-DSH-001](../../02_technical_specs/dashboard/TP-DSH-001.md)
- [Glossary](../../../glossary.md)
