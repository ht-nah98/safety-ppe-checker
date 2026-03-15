# Product Backlog: Safety PPE Checker

> Cập nhật lần cuối: 2026-03-15

---

## Backlog Overview

| Status | Count |
|--------|-------|
| Must Have | 7 stories |
| Should Have | 5 stories |
| Nice to Have | 3 stories |
| Total | 15 stories |

---

## SPRINT 1 — Backend + CV Engine (22–28/03/2026)

| ID | Story | Priority | Points | Status |
|----|-------|----------|--------|--------|
| US-CV-001 | Detect mũ bảo hộ trong ảnh | Must Have | 3 | ⬜ Todo |
| US-CV-002 | Detect áo phản quang trong ảnh | Must Have | 2 | ⬜ Todo |
| US-CV-003 | Trả về pass/fail tổng thể + từng hạng mục | Must Have | 3 | ⬜ Todo |
| US-CV-004 | Bounding box trực quan trên ảnh kết quả | Should Have | 2 | ⬜ Todo |

---

## SPRINT 2 — Frontend Web UI (29/03–04/04/2026)

| ID | Story | Priority | Points | Status |
|----|-------|----------|--------|--------|
| US-WEB-001 | Upload ảnh từ máy tính để kiểm tra | Must Have | 3 | ⬜ Todo |
| US-WEB-002 | Chụp ảnh trực tiếp từ webcam | Should Have | 3 | ⬜ Todo |
| US-WEB-003 | Xem kết quả rõ ràng: pass/fail + màu sắc | Must Have | 2 | ⬜ Todo |
| US-WEB-004 | Xem chi tiết từng hạng mục bị thiếu | Must Have | 2 | ⬜ Todo |
| US-WEB-005 | Trang kết quả dễ screenshot để lưu hồ sơ | Nice to Have | 1 | ⬜ Todo |

---

## SPRINT 3 — Dashboard + Polish (05–12/04/2026)

| ID | Story | Priority | Points | Status |
|----|-------|----------|--------|--------|
| US-DSH-001 | Xem danh sách lịch sử kiểm tra theo thời gian | Must Have | 3 | ⬜ Todo |
| US-DSH-002 | Xem thống kê: tổng pass/fail, vi phạm nhiều nhất | Should Have | 3 | ⬜ Todo |
| US-DSH-003 | Export báo cáo CSV đơn giản | Nice to Have | 2 | ⬜ Todo |

---

## FUTURE (Phase 2 — sau demo)

| ID | Story | Lý do để sau |
|----|-------|--------------|
| US-ADV-001 | Pose estimation — verify PPE đúng vị trí | Phức tạp, không cần cho demo |
| US-ADV-002 | Nhận diện danh tính nhân viên | Cần data thực từ công ty |
| US-ADV-003 | Multi-job-type checklist | Cần nghiệp vụ từ khách hàng |
| US-ADV-004 | Mobile app native | Sau khi có feedback từ demo |
| US-ADV-005 | Tích hợp hệ thống HR | Cần API từ hệ thống của công ty |

---

## Story Points Summary

| Sprint | Total Points | Notes |
|--------|-------------|-------|
| Sprint 1 | 10 | CV Engine core |
| Sprint 2 | 11 | Full web UI |
| Sprint 3 | 8 | Dashboard + polish |
| **Total** | **29** | 4 tuần |
