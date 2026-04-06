# Báo Cáo Kết Quả Huấn Luyện Mô Hình Kiểm Tra Bảo Hộ Lao Động (PPE)

## 1. Tổng Quan (Executive Summary)
Dự án **Safety PPE Checker** đã hoàn thành giai đoạn huấn luyện mô hình nhận diện thiết bị bảo hộ lao động (mũ bảo hiểm, áo phản quang, v.v.). Kết quả huấn luyện cho thấy mô hình đạt độ chính xác cao, sẵn sàng cho việc triển khai thử nghiệm (Beta testing) và tích hợp vào hệ thống giám sát thời gian thực.

**Các điểm chính:**
- **Độ chính xác (Precision):** 85.7% - Đảm bảo ít cảnh báo sai.
- **Độ bao phủ (Recall):** 68.7% - Nhận diện tốt phần lớn các lỗi vi phạm.
- **Tính ổn định:** Mô hình đã hội tụ sau 100 epoch với hàm mất mát (loss) thấp.

---

## 2. Cấu Hình Huấn Luyện (Training Configuration)
Việc huấn luyện được thực hiện với các tham số tối ưu để cân bằng giữa tốc độ xử lý và độ chính xác.

| Tham số | Giá trị |
| :--- | :--- |
| **Model Architecture** | YOLOv8s (Small) |
| **Input Size** | 640x640 pixels |
| **Epochs** | 100 |
| **Batch Size** | 16 |
| **Optimizer** | Auto (Stochastic Gradient Descent) |
| **Augmentation** | Mosaic, Flip, HSV scaling |

---

## 3. Chỉ Số Hiệu Năng (Performance Metrics)

### 3.1. Các Chỉ Số Chính
Kết quả tại epoch cuối cùng (100):

- **mAP@50:** **0.748** (Khả năng nhận diện vật thể ở mức tin cậy 50% IoU).
- **mAP@50-95:** **0.547** (Độ chính xác về vị trí khung bao - Bounding Box).

### 3.2. Đồ Thị Kết Quả (Results Overview)
Đồ thị dưới đây cho thấy sự thay đổi của các hàm mất mát và độ chính xác qua 100 vòng lặp (epochs). Các đường cong hội tụ ổn định, không có dấu hiệu Overfitting.

![Kết quả huấn luyện qua 100 epoch](assets/results.png)

### 3.3. Biểu đồ Chất lượng (Quality Curves) - CẬP NHẬT ĐẦY ĐỦ
Đây là các chỉ số quan trọng nhất để đánh giá hiệu năng mô hình tại các ngưỡng tin cậy khác nhau:

- **Precision-Recall Curve:** Đánh giá sự cân bằng giữa độ chính xác và khả năng tìm thấy vật thể.
  ![PR Curve](assets/BoxPR_curve.png)

- **F1-Confidence Curve:** Tìm ngưỡng tin cậy tối ưu để đạt F1-score cao nhất.
  ![F1 Curve](assets/BoxF1_curve.png)

- **Precision-Confidence Curve:** Độ chính xác của mô hình tăng dần theo ngưỡng tin cậy.
  ![Precision Curve](assets/BoxP_curve.png)

- **Recall-Confidence Curve:** Khả năng bao phủ của mô hình tại các mức tin cậy.
  ![Recall Curve](assets/BoxR_curve.png)

---

## 4. Phân Tích Chi Tiết (Detailed Analysis)

### 4.1. Ma Trận Nhầm Lẫn (Confusion Matrix)
Ma trận này giúp xác định các lớp mà mô hình hay nhầm lẫn nhất.
![Ma trận nhầm lẫn](assets/confusion_matrix.png)

---

## 5. Kết Quả Thực Tế (Visual Validation)
Dưới đây là các mẫu kết quả dự đoán thực tế từ hệ thống:

![Mẫu dự đoán 1](assets/val_batch0_pred.jpg)
![Mẫu dự đoán 2](assets/val_batch1_pred.jpg)
![Mẫu dự đoán 3](assets/val_batch2_pred.jpg)

---

## 6. Đánh Giá & Hành Động Tiếp Theo (Next Actions)

### Đánh giá chất lượng:
Mô hình đạt mức **"Khá - Tốt"**. Với độ chính xác 85.7%, hệ thống có thể hoạt động tin cậy trong thực tế mà không gây phiền nhiễu bởi các cảnh báo giả.

### Các bước tiếp theo:
1. **Triển khai thực địa (Field Deployment):** Tích hợp model `ppe_v1_final` vào backend để chạy thực tế trên camera.
2. **Thu thập dữ liệu biên (Edge cases):** Tiếp tục thu thập hình ảnh ở các góc quay khó hoặc điều kiện thiếu sáng để fine-tune trong phiên bản v2.
3. **Tối ưu hóa (Optimization):** Chuyển đổi mô hình sang định dạng TensorRT hoặc OpenVINO để tăng tốc độ xử lý trên phần cứng chuyên dụng.

---
**Người lập báo cáo:** Antigravity (AI Assistant)
**Ngày:** 02/04/2026
