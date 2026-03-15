# Test Strategy: Safety PPE Checker

> **Status**: Draft
> **Version**: 1.0
> **Date**: 2026-03-15
> **Target Milestone**: Demo Release (2026-04-12)

---

## 1. Overview

Tài liệu này định nghĩa chiến lược kiểm thử cho dự án **Safety PPE Checker**. Mục tiêu là đảm bảo hệ thống hoạt động ổn định, AI detect chính xác và trải nghiệm người dùng mượt mà trong buổi demo.

## 2. Test Objectives

1. **Verify AI Accuracy**: Đảm bảo YOLOv8 detect đúng 5 hạng mục PPE với mAP50 ≥ 80%.
2. **Verify Functional Requirements**: Test đầy đủ các tính năng Upload, Camera, Results, Dashboard.
3. **Validate Business Logic**: Kiểm tra logic định nghĩa PASS/FAIL (phải đủ 5/5 items mới PASS).
4. **Performance Check**: Đảm bảo thời gian xử lý ảnh < 3 giây.
5. **Stability**: Demo không bị crash khi gặp input sai format hoặc lỗi mạng.

## 3. Scope of Testing

### In Scope
* **CV Engine**: Accuracy, Confidence, Inference Time, Annotated Image output.
* **Web Interface**: File Upload (Drag & Drop), Webcam Integration, UI State (Loading/Error/Success).
* **Backend API**: Contract validation, Database persistence (SQLite), Stats calculation.
* **Integration**: End-to-end flow từ upload đến hiển thị trên Dashboard.

### Out of Scope
* Security testing (Auth, SQL Injection, etc. - do là bản demo).
* Load testing (> 10 concurrent users).
* Cross-browser testing ngoài Chrome/Firefox.
* Mobile Native testing.

## 4. Test Levels

| Level | Description | Tool | Responsibility |
|-------|-------------|------|----------------|
| **Unit Test** | Test các function logic nhỏ (pass/fail logic, class mapping) | Pytest | Developer |
| **API Test** | Test endpoint `/api/v1/check-ppe` với các input khác nhau | Postman / Curl | Developer |
| **CV Evaluation** | Đánh giá model trên Valid/Test dataset | YOLOv8 Val mode | Developer |
| **E2E Test** | Test toàn bộ luồng từ UI người dùng | Manual Testing | PO / Developer |
| **Demo Prep** | Chạy thử kịch bản demo 15 phút | Manual | PO |

## 5. Test Scenarios (Tổng quát)

### 5.1 CV Engine (AI Logic)
* **SC-CV-01**: Ảnh đầy đủ 5 PPE -> Expect all detected.
* **SC-CV-02**: Ảnh thiếu 1 hoặc nhiều PPE -> Expect missing items correctly identified.
* **SC-CV-03**: Ảnh không có người/nhiều người -> Expect handling logic.
* **SC-CV-04**: Ảnh độ phân giải thấp/mờ -> Expect confidence warning.

### 5.2 Web Frontend
* **SC-WEB-01**: Upload file PNG/JPG hợp lệ.
* **SC-WEB-02**: Chụp ảnh từ Camera (verify permission).
* **SC-WEB-03**: Hiển thị kết quả (Color coding: Green for PASS, Red for FAIL).
* **SC-WEB-04**: Handling file quá lớn (> 10MB) hoặc sai định dạng (.pdf, .exe).

### 5.3 Dashboard & Stats
* **SC-DSH-01**: Lưu lịch sử sau mỗi lượt check.
* **SC-DSH-02**: Tính toán stats (Tổng lượt, tỷ lệ %) chính xác.
* **SC-DSH-03**: Export CSV chứa data khớp với DB.

## 6. Test Data

Hệ thống sử dụng bộ 20 ảnh demo chuẩn bị sẵn:
* **5 PASS images**: Đầy đủ trang bị, rõ nét.
* **10 FAIL images**: Mỗi ảnh thiếu 1-2 món khác nhau.
* **3 EDGE images**: Ánh sáng yếu, góc nghiêng hoặc ảnh có vật cản.
* **2 INVALID items**: File không phải ảnh hoặc file rỗng.

## 7. Acceptance Criteria (Testing Perspective)

* [ ] **Accuracy**: ≥ 85% trên 20 ảnh demo.
* [ ] **Speed**: Average processing time < 3s.
* [ ] **UX**: Trạng thái PASS/FAIL hiển thị rõ ràng trong vòng 1 giây sau khi có kết quả API.
* [ ] **Data**: Mọi giao dịch thành công đều xuất hiện trong Dashboard.

---

## 8. Defect Management

Do tính chất dự án demo ngắn hạn:
* Lỗi nghiêm trọng (Crash, AI sai hoàn toàn): Fix ngay lập tức.
* Lỗi UI nhỏ (Căn lề, màu sắc): Fix trước buổi demo 2 ngày.
* Improvement (Thêm tính năng): Note vào Backlog (Phase 2).
