# PROJECT INSIGHTS: Safety PPE Checker

> **Document**: INSIGHTS-AND-TIPS.md
> **Purpose**: Tổng hợp toàn bộ kinh nghiệm, mẹo và quy tắc để tránh sai sót trong quá trình phát triển dự án PPE.

---

## 💡 AI/CV Tips (The Core Engine)

1. **Mapping Class là sống còn**:
    * Đừng bao giờ tin vào class name mặc định của dataset. Phải map `hardhat` → `helmet`, `vest` → `reflective_vest`.
    * Luôn check `dataset.yaml` trước khi train để đảm bảo ID class khớp với code backend.

2. **Confidence Threshold - "Con dao hai lưỡi"**:
    * Với demo, đừng để threshold quá cao (0.5). Với những item nhỏ như **Găng tay** hay **Kính**, hãy thử ở mức **0.35 - 0.4** để tránh False Negative (báo thiếu dù có mặt).
    * `helmet` và `vest` có thể để **0.5 - 0.6** vì chúng rất rõ ràng.

3. **Data Augmentation - Mẹo cho ảnh demo**:
    * Khi chuẩn bị ảnh demo, hãy dùng ảnh có độ phân giải từ **640x640** trở lên. YOLOv8 mặc định resize về 640. Nếu ảnh quá nhỏ, AI sẽ "mờ mắt" với găng tay.

---

## 🎨 UI/UX Tricks (The Wow Factor)

1. **Màu sắc tâm lý**:
    * Dùng mã màu chuyên nghiệp thay vì màu thuần:
        * Success: `#10B981` (Emerald 500)
        * Danger: `#EF4444` (Red 500)
    * Dashboard nên dùng Dark Mode hoặc Glassmorphism để tạo cảm giác "Industry 4.0".

2. **Loading States**:
    * Demo AI mà đợi 3 giây màn hình trắng là thất bại. Hãy dùng 1 cái "Scanning Animation" (một tia laser quét qua ảnh) để tạo cảm giác AI đang thực sự làm việc.

3. **Screenshot Mode**:
    * Thêm 1 nút "Tải kết quả (PDF/JPG)" ở trang kết quả. Giám sát viên sẽ rất thích tính năng này để gửi vào group Zalo báo cáo.

---

## 🛠️ Code Architecture Guardrails

1. **Backend - FastAPI**:
    * Dùng `BackgroundTasks` để lưu DB hoặc copy ảnh, đừng để user phải đợi DB ghi xong mới thấy kết quả AI.
    * Luôn có `inspection_id` duy nhất cho mỗi lượt check để truy vết.

2. **Database**:
    * Mặc dù dùng SQLite cho demo, hãy thiết kế Schema sao cho dễ migrate lên PostgreSQL (dùng SQLAlchemy).

---

## ⚠️ Common Mistakes to Avoid

* ❌ **Quên check Camera Permission**: Luôn phải handle trường hợp user nhấn "Deny" trên browser.
* ❌ **Inference trên CPU bị nghẽn**: Nếu chạy local, nhớ tắt các app nặng. Nếu chạy Docker, giới hạm RAM ít nhất 4GB cho container backend.
* ❌ **Class Overlap**: Helmet và Head thường bị chồng lấn. Nhớ dùng NMS (Non-Maximum Suppression) chuẩn của YOLO.

---

## 📋 Prompt Engineering for Next Steps

Khi yêu cầu thực hiện bước tiếp theo, hãy nhắc lại quy tắc này:
> "Sử dụng skill `ppe_project_guardrails` và tham khảo mapping class trong `DATA-STRATEGY.md`."
