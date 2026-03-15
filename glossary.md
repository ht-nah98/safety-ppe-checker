# Glossary: Safety PPE Checker

> Thuật ngữ và viết tắt sử dụng trong dự án. AI tham khảo file này để đảm bảo consistency.

---

## Viết tắt (Abbreviations)

| Viết tắt | Full Form | Giải thích |
|----------|-----------|------------|
| PPE | Personal Protective Equipment | Trang bị bảo hộ cá nhân |
| CV | Computer Vision | Thị giác máy tính |
| AI | Artificial Intelligence | Trí tuệ nhân tạo |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| YOLO | You Only Look Once | Thuật toán object detection real-time |
| mAP | Mean Average Precision | Metric đo accuracy của object detection model |
| FN | False Negative | Hệ thống không phát hiện vi phạm trong khi thực tế có vi phạm |
| FP | False Positive | Hệ thống báo vi phạm trong khi thực tế không vi phạm |
| MVP | Minimum Viable Product | Sản phẩm khả thi tối thiểu |
| PRD | Product Requirements Document | Tài liệu yêu cầu sản phẩm |
| US | User Story | Câu chuyện người dùng |
| AC | Acceptance Criteria | Tiêu chí chấp nhận |
| DoD | Definition of Done | Định nghĩa hoàn thành |
| TP | Technical Specification | Tài liệu đặc tả kỹ thuật |

---

## Thuật ngữ nghiệp vụ (Business Terms)

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| Trang bị bảo hộ (PPE) | Các thiết bị bảo vệ cá nhân bắt buộc khi làm việc ngành điện: mũ bảo hộ, áo phản quang, găng tay, giày bảo hộ, kính bảo hộ |
| Tuân thủ PPE | Trạng thái nhân viên đã mặc đầy đủ tất cả các hạng mục PPE bắt buộc theo quy định |
| Vi phạm PPE | Trạng thái nhân viên thiếu ít nhất 1 hạng mục PPE bắt buộc |
| Kiểm tra PPE | Quá trình chụp ảnh và đánh giá tự động xem nhân viên có đủ PPE không |
| Audit trail | Lịch sử kiểm tra được lưu trữ, bao gồm thời gian, ảnh, kết quả — dùng để truy vết và báo cáo |
| Checklist PPE | Danh sách các hạng mục PPE bắt buộc cần kiểm tra |
| Mũ bảo hộ | Helmet / Hard hat — bảo vệ đầu khỏi va đập và điện giật |
| Áo phản quang | Reflective vest / Hi-vis vest — áo có vạch phản quang, dễ nhận diện |
| Găng tay bảo hộ | Safety gloves — bảo vệ tay khỏi điện giật và vật sắc nhọn |
| Giày bảo hộ | Safety boots — giày cách điện, bảo vệ chân |
| Kính bảo hộ | Safety glasses / Goggles — bảo vệ mắt khỏi tia lửa, hóa chất |

---

## Thuật ngữ kỹ thuật (Technical Terms)

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| Object Detection | Kỹ thuật CV xác định vị trí và phân loại vật thể trong ảnh |
| Bounding Box | Hộp chữ nhật bao quanh vật thể được detect trong ảnh |
| Confidence Score | Điểm tin cậy (0.0–1.0) thể hiện mức độ chắc chắn của model khi detect một object |
| Confidence Threshold | Ngưỡng confidence tối thiểu để xác nhận detection (mặc định: 0.5) |
| Inference | Quá trình chạy model AI trên một ảnh để lấy kết quả detect |
| Fine-tuning | Quá trình huấn luyện thêm model pretrained trên dataset riêng của project |
| Pretrained Model | Model đã được huấn luyện sẵn trên dataset lớn, có thể dùng ngay hoặc fine-tune |
| YOLOv8n | Phiên bản nano của YOLOv8 — nhỏ nhất, nhanh nhất, phù hợp demo |
| Roboflow | Nền tảng quản lý dataset CV, có sẵn nhiều PPE dataset public |
| Annotated Image | Ảnh đầu ra đã được vẽ bounding box và nhãn lên kết quả detect |
| Data Augmentation | Kỹ thuật tăng cường dataset bằng cách biến đổi ảnh (lật, xoay, thay độ sáng...) |
| Class Mapping | Quá trình chuyển đổi tên class từ dataset ngoài sang class chuẩn của project |
| Pose Estimation | Kỹ thuật xác định vị trí các khớp xương người — dùng để verify PPE đúng vị trí (Phase 2) |
| FastAPI | Python web framework tốc độ cao, phù hợp cho ML backend |
| Docker Compose | Công cụ chạy nhiều container Docker cùng lúc bằng 1 file config |
| SQLite | Database file-based nhẹ, không cần cài đặt server — dùng cho dev/demo |

---

## Quy ước đặt tên (Naming Conventions)

### Documents
```
PRD:            PRD-[name].md               → PRD-safety-ppe-checker.md
Epic:           EPIC-[PREFIX]-[N].md        → EPIC-CV-001.md
User Story:     US-[PREFIX]-[N].md          → US-CV-001.md
Tech Spec:      TP-[PREFIX]-[N].md          → TP-CV-001.md
Test Case:      TC-[PREFIX]-[N].md          → TC-CV-001.md
```

### Module Prefixes
```
CV  → CV Engine (Computer Vision)
WEB → Web Interface (Frontend)
DSH → Dashboard
API → Backend API
```

### PPE Class Names (chuẩn trong code)
```
helmet            → Mũ bảo hộ
reflective_vest   → Áo phản quang
gloves            → Găng tay bảo hộ
safety_boots      → Giày bảo hộ
safety_glasses    → Kính bảo hộ
```

---

> **Hướng dẫn**: Cập nhật file này khi xuất hiện thuật ngữ mới. AI tham khảo file này để đảm bảo consistency trong toàn bộ tài liệu dự án.
