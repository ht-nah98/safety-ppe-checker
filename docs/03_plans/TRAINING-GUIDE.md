# Hướng Dẫn Huấn Luyện Mô Hình PPE Detection

> **Dành cho:** Người mới bắt đầu, chưa có kinh nghiệm về AI/ML
> **Mục tiêu:** Fine-tune YOLOv8 để nhận diện 5 thiết bị bảo hộ lao động
> **Môi trường:** Máy tính cá nhân (local machine)
> **Thời gian dự kiến:** 3–6 giờ (bao gồm tải dataset và training)

---

## Mục Lục

1. [Hiểu Tổng Quan Trước Khi Bắt Đầu](#1-hiểu-tổng-quan-trước-khi-bắt-đầu)
2. [Phase 0 — Cài Đặt Môi Trường](#phase-0--cài-đặt-môi-trường)
3. [Phase 1 — Tải Dataset](#phase-1--tải-dataset)
4. [Phase 2 — Gộp và Chuyển Đổi Nhãn](#phase-2--gộp-và-chuyển-đổi-nhãn)
5. [Phase 3 — Kiểm Tra Cấu Hình](#phase-3--kiểm-tra-cấu-hình)
6. [Phase 4 — Huấn Luyện Mô Hình](#phase-4--huấn-luyện-mô-hình)
7. [Phase 5 — Đánh Giá Kết Quả](#phase-5--đánh-giá-kết-quả)
8. [Phase 6 — Tích Hợp Vào Backend](#phase-6--tích-hợp-vào-backend)
9. [Phase 7 — Kiểm Tra Trên Giao Diện](#phase-7--kiểm-tra-trên-giao-diện)
10. [Xử Lý Lỗi Thường Gặp](#xử-lý-lỗi-thường-gặp)
11. [Giải Thích Thuật Ngữ](#giải-thích-thuật-ngữ)

---

## 1. Hiểu Tổng Quan Trước Khi Bắt Đầu

### Hiện tại ứng dụng đang dùng gì?

Hiện tại backend đang dùng **YOLOv8n với COCO weights** — đây là mô hình nhận diện vật thể tổng quát, được huấn luyện để nhận ra 80 loại đồ vật thông thường như xe hơi, chó, con người... **Nó chưa bao giờ thấy mũ bảo hộ hay áo phản quang**, nên kết quả trả về gần như luôn sai.

### Chúng ta sẽ làm gì?

Chúng ta sẽ **fine-tune** (tinh chỉnh) mô hình này trên hàng nghìn ảnh công nhân mặc PPE có gán nhãn sẵn. Sau khi training xong, chúng ta copy 1 file (`best.pt`) vào thư mục backend. Backend tự động dùng file mới đó — **không cần thay đổi gì trên Frontend hay UI**.

### Fine-tuning là gì?

Hãy tưởng tượng bạn thuê một bác sĩ đa khoa (mô hình COCO) và cho họ học thêm chuyên khoa bảo hộ lao động (fine-tune trên dataset PPE). Bác sĩ đó đã có nền tảng y khoa tốt, chỉ cần học thêm chuyên môn. Nhanh hơn rất nhiều so với đào tạo từ đầu.

### Luồng hoạt động sau khi training:

```
Ảnh worker upload
      ↓
Backend (FastAPI)
      ↓
cv_engine.py → load best.pt (mô hình đã train)
      ↓
YOLOv8 phát hiện helmet, vest, gloves, boots, glasses
      ↓
So sánh với ngưỡng confidence (config.py)
      ↓
Trả về PASS/FAIL + JSON kết quả
      ↓
Frontend hiển thị (không cần thay đổi gì)
```

### 5 lớp PPE chúng ta cần nhận diện:

| ID | Tên tiêu chuẩn | Tiếng Việt |
|---|---|---|
| 0 | `helmet` | Mũ bảo hộ |
| 1 | `reflective_vest` | Áo phản quang |
| 2 | `gloves` | Găng tay bảo hộ |
| 3 | `safety_boots` | Giày bảo hộ |
| 4 | `safety_glasses` | Kính bảo hộ |

---

## ✅ TRẠNG THÁI HIỆN TẠI (PHẢI ĐỌC)

Tôi đã hoàn thành việc chuẩn bị dữ liệu cho bạn:
1. **Dataset:** Đã tải và giải nén 2 bộ dữ liệu (Construction-PPE và SH17).
2. **Gộp dữ liệu:** Đã chạy script gộp và chuẩn bị xong **7,237 ảnh training** (với nhãn đã được chuẩn chuẩn hóa về 5 lớp 0-4).
3. **Cấu hình:** File `data/dataset.yaml` đã sẵn sàng.

**Bạn có thể BỎ QUA Phase 1 và Phase 2 trong hướng dẫn này và bắt đầu ngay từ Phase 0 (Cài môi trường) sau đó nhảy đến Phase 3.**

---

## Phase 0 — Cài Đặt Môi Trường

### Bước 0.0 — Tạo và kích hoạt môi trường ảo (BẮT BUỘC)

Như bạn đã hỏi, **RẤT NÊN** tạo môi trường ảo riêng (`venv`) để tránh xung đột với các thư viện khác trên máy.

```bash
# Đảm bảo đang ở thư mục gốc của dự án
cd /home/user/Desktop/safety-ppe-checker

# Tạo môi trường ảo tên là venv_ppe
python3 -m venv venv_ppe

# Kích hoạt môi trường ảo
source venv_ppe/bin/activate
```

Sau khi kích hoạt, bạn sẽ thấy chữ `(venv)` ở đầu dòng lệnh terminal.

### Bước 0.1 — Cài thư viện cần thiết

Khi đã ở trong môi trường ảo, chạy lệnh sau để cài đặt:

```bash
pip install --upgrade pip
pip install ultralytics roboflow pyyaml
```

- **ultralytics**: Thư viện chứa YOLOv8 — dùng để training và inference
- **roboflow**: Tool tải dataset từ Roboflow.com
- **pyyaml**: Đọc file `.yaml` trong Python

### Bước 0.2 — Kiểm tra GPU

```bash
python -c "import torch; print('GPU:', torch.cuda.is_available())"
```

**Kết quả `GPU: True`** → Bạn có GPU, training sẽ mất 1–3 giờ. Tiếp tục bình thường.

**Kết quả `GPU: False`** → Không có GPU. Bạn có 2 lựa chọn:

> **Lựa chọn A — Dùng Google Colab (Miễn phí, Khuyến nghị)**
>
> 1. Truy cập https://colab.research.google.com
> 2. Tạo notebook mới
> 3. Vào menu: **Runtime → Change runtime type → T4 GPU → Save**
> 4. Chạy tất cả lệnh training trong notebook đó
> 5. Sau khi xong, tải file `best.pt` về máy và copy vào `backend/models_weights/`
>
> **Lựa chọn B — Train trên CPU**
>
> Vẫn chạy được nhưng sẽ mất 10–20 giờ. Không khuyến nghị.

### Bước 0.3 — Kiểm tra cấu trúc thư mục

```bash
# Đảm bảo bạn đang ở thư mục gốc của dự án
cd /home/user/Desktop/safety-ppe-checker

# Kiểm tra các thư mục cần thiết tồn tại
ls data/
# Kết quả phải có: dataset.yaml  demo/

ls backend/models_weights/
# Thư mục này hiện đang trống — sau training sẽ có best.pt
```

---

## Phase 1 — Tải Dataset

Chúng ta cần ảnh có gán nhãn (labeled images). "Gán nhãn" nghĩa là mỗi ảnh có một file `.txt` kèm theo, ghi tọa độ của từng vật thể trong ảnh và tên lớp của nó. Chúng ta **không tự tạo nhãn** — tải dataset có sẵn từ Roboflow.

### Hai dataset sẽ dùng:

| Dataset | Số ảnh | Lý do dùng |
|---|---|---|
| **Construction-PPE** | ~1,400 ảnh | Có đủ cả 5 lớp PPE của chúng ta |
| **SH17** | ~8,000 ảnh | Thêm data, đặc biệt quan trọng cho găng tay và kính (vật nhỏ, khó nhận diện) |

### Bước 1.1 — Tạo thư mục lưu dataset

```bash
# Chạy từ thư mục gốc dự án
mkdir -p data/raw
```

### Bước 1.2 — Lựa chọn tải Dataset

Có 2 cách để lấy dữ liệu. Nếu bạn không dùng được API Key hoặc script bị lỗi, hãy dùng **Cách B (Thủ công)**.

#### Cách A — Dùng Script (Nếu API hoạt động)
*(Giữ nguyên các bước python như cũ trong file này)*

#### Cách B — Tải Thủ Công (Khuyên dùng nếu Cách A lỗi)

1. **Truy cập đường dẫn Roboflow:**
   - **Dataset 1 (Construction-PPE):** [Construction-PPE Detection](https://universe.roboflow.com/construction-ppe/construction-ppe-detection/dataset/1)
   - **Dataset 2 (SH17):** [SH17 Dataset](https://universe.roboflow.com/roboflow-universe-projects/sh17-dataset/dataset/1)

2. **Cách tải trên Web:**
   - Nhấn nút **Download Dataset** (góc trên bên phải).
   - Chọn Format: **YOLOv8**.
   - Chọn **download zip to computer**.
   - Nhấn **Continue** và đợi file tải về.

3. **Giải nén và sắp xếp:**
   - Giải nén file zip của Construction-PPE vào thư mục: `data/raw/construction-ppe/`
   - Giải nén file zip của SH17 vào thư mục: `data/raw/sh17/`

**Cấu trúc thư mục đúng sẽ trông như thế này:**
```text
data/
└── raw/
    ├── construction-ppe/
    │   ├── train/
    │   ├── val/
    │   ├── test/
    │   └── data.yaml
    └── sh17/
        ├── train/
        ├── val/
        ├── test/
        └── data.yaml
```

### Bước 1.3 — Tải Construction-PPE dataset

```bash
cd data/raw

python - <<'EOF'
from roboflow import Roboflow

# Thay YOUR_API_KEY bằng API key của bạn
rf = Roboflow(api_key="YOUR_API_KEY")

project = rf.workspace("construction-ppe").project("construction-ppe-detection")
version = project.version(1)
dataset = version.download("yolov8", location="construction-ppe")

print("Tải xong! Đã lưu vào data/raw/construction-ppe/")
EOF
```

### Bước 1.4 — Tải SH17 dataset

```bash
# Vẫn đang ở data/raw/

python - <<'EOF'
from roboflow import Roboflow

rf = Roboflow(api_key="YOUR_API_KEY")

project = rf.workspace("roboflow-universe-projects").project("sh17-dataset")
version = project.version(1)
dataset = version.download("yolov8", location="sh17")

print("Tải xong! Đã lưu vào data/raw/sh17/")
EOF
```

### Bước 1.5 — Xác nhận download thành công

```bash
# Quay về thư mục gốc
cd ../..

# Kiểm tra cấu trúc
ls data/raw/construction-ppe/
# Phải thấy: train/   val/   test/   data.yaml

ls data/raw/sh17/
# Phải thấy: train/   val/   test/   data.yaml

# Kiểm tra số lượng ảnh
ls data/raw/construction-ppe/train/images/ | wc -l
# Khoảng 900-1100 ảnh

ls data/raw/sh17/train/images/ | wc -l
# Khoảng 5000-7000 ảnh
```

### Bước 1.6 — QUAN TRỌNG: Xem danh sách lớp của từng dataset

```bash
cat data/raw/construction-ppe/data.yaml
```

Bạn sẽ thấy dạng như thế này:

```yaml
nc: 8
names: ['helmet', 'no_helmet', 'vest', 'no_vest', 'gloves', 'no_gloves', 'boots', 'glasses']
#        ID=0       ID=1         ID=2    ID=3        ID=4      ID=5         ID=6     ID=7
```

```bash
cat data/raw/sh17/data.yaml
```

```yaml
nc: 17
names: ['hard-hat', 'gloves', 'jacket', 'keyboard', 'laptop', 'person', 'phone',
        'shoes', 'ear-protector', 'safety-vest', ...]
#        ID=0        ID=1          ID=2    ...                             ID=9
```

**Ghi lại ID của các lớp PPE** trong mỗi dataset. Bạn sẽ cần ở bước tiếp theo.

---

## Phase 2 — Gộp và Chuyển Đổi Nhãn

### Vì sao cần bước này?

Mỗi dataset dùng số ID khác nhau cho cùng một vật thể. Ví dụ:
- Construction-PPE: `helmet = 0`, `vest = 2`
- SH17: `hard-hat = 0`, `safety-vest = 9`

Chúng ta phải chuyển tất cả về **ID tiêu chuẩn của dự án** (0=helmet, 1=vest, 2=gloves, 3=boots, 4=glasses) trước khi training.

### Bước 2.1 — Cập nhật CLASS_REMAP trong script

Mở file `scripts/prepare_dataset.py`. Tìm đến phần `CLASS_REMAP` (khoảng dòng 60).

So sánh với kết quả bạn đọc được ở Bước 1.6, cập nhật các số ID cho đúng.

**Ví dụ:** Nếu `data/raw/construction-ppe/data.yaml` cho thấy:
```
names: ['helmet', 'no_helmet', 'vest', 'no_vest', 'gloves', 'no_gloves', 'boots', 'glasses']
```

Thì mapping đúng là:
```python
("construction-ppe", 0): 0,   # helmet (ID=0) → canonical helmet (0)
("construction-ppe", 2): 1,   # vest   (ID=2) → canonical reflective_vest (1)
("construction-ppe", 4): 2,   # gloves (ID=4) → canonical gloves (2)
("construction-ppe", 6): 3,   # boots  (ID=6) → canonical safety_boots (3)
("construction-ppe", 7): 4,   # glasses(ID=7) → canonical safety_glasses (4)
# ID=1,3,5 (no_helmet, no_vest, no_gloves) → BỎ QUA (lớp âm tính)
```

> **Lưu ý:** Nếu ID trong file bạn download khác với ví dụ trên, hãy cập nhật lại cho đúng. Đây là bước dễ sai nhất.

### Bước 2.2 — Chạy script gộp dataset

```bash
# Từ thư mục gốc dự án
python scripts/prepare_dataset.py
```

Output mẫu khi thành công:

```
INFO: === Class mapping verification ===
INFO:   construction-ppe classes:
INFO:     [ 0] helmet                    → canonical 0
INFO:     [ 1] no_helmet                   (skipped)
INFO:     [ 2] vest                      → canonical 1
INFO:     [ 3] no_vest                     (skipped)
INFO:     [ 4] gloves                    → canonical 2
INFO:     [ 5] no_gloves                   (skipped)
INFO:     [ 6] boots                     → canonical 3
INFO:     [ 7] glasses                   → canonical 4
INFO: Processing: construction-ppe
INFO:   construction-ppe    train → 987 images
INFO:   construction-ppe    val   → 198 images
INFO:   construction-ppe    test  → 201 images
INFO: Processing: sh17
INFO:   sh17               train → 6234 images
INFO:   sh17               val   → 1189 images
INFO:   sh17               test  → 676 images
INFO: === Dataset merge summary ===
INFO:   train total: 7221 images
INFO:   val   total: 1387 images
INFO:   test  total: 877 images
INFO: Validation PASSED — all class IDs in [0, 4]
```

### Bước 2.3 — Xác nhận kết quả

```bash
# Kiểm tra số lượng ảnh đã gộp
ls data/processed/train/images/ | wc -l   # Phải >= 6000
ls data/processed/val/images/   | wc -l   # Phải >= 1000

# Kiểm tra nhãn có đúng format không
head data/processed/train/labels/construction-ppe_worker_001.txt
```

Mỗi dòng trong file nhãn phải có dạng:
```
0 0.512 0.234 0.145 0.089
1 0.321 0.567 0.234 0.456
```

Cột đầu tiên là class ID (chỉ được là 0, 1, 2, 3, hoặc 4). Các cột còn lại là tọa độ bounding box (giá trị 0.0–1.0).

---

## Phase 3 — Kiểm Tra Cấu Hình

### Bước 3.1 — Xác nhận file dataset.yaml

```bash
cat data/dataset.yaml
```

Phải thấy đúng nội dung này:

```yaml
path: ./data/processed
train: train/images
val:   val/images
test:  test/images
nc: 5
names:
  0: helmet
  1: reflective_vest
  2: gloves
  3: safety_boots
  4: safety_glasses
```

Nếu thứ tự `names` bị khác → dừng lại, sửa cho đúng rồi mới training. Thứ tự này phải khớp hoàn toàn với CLASS_REMAP ở Phase 2.

### Bước 3.2 — Chọn kích thước mô hình

| Mô hình | Độ chính xác | RAM GPU cần | Tốc độ inference |
|---|---|---|---|
| `yolov8n.pt` | ~65–70% mAP | 4 GB | Nhanh nhất |
| **`yolov8s.pt`** | **~75–80% mAP** | **6 GB** | **Nhanh** |
| `yolov8m.pt` | ~80–85% mAP | 10 GB | Vừa |

**Khuyến nghị: dùng `yolov8s.pt`** — cân bằng tốt giữa độ chính xác và tốc độ.

Nếu máy bạn RAM dưới 6GB thì dùng `yolov8n.pt`.

---

## Phase 4 — Huấn Luyện Mô Hình

### Giải thích các tham số training:

| Tham số | Ý nghĩa |
|---|---|
| `data=data/dataset.yaml` | Đường dẫn đến file cấu hình dataset |
| `model=yolov8s.pt` | Mô hình gốc để fine-tune (tự download nếu chưa có) |
| `epochs=100` | Số lần duyệt qua toàn bộ dataset |
| `imgsz=640` | Resize ảnh về 640×640 pixel trước khi training |
| `batch=16` | Xử lý 16 ảnh cùng lúc. Giảm xuống 8 nếu bị lỗi bộ nhớ |
| `patience=20` | Dừng sớm nếu 20 epoch liên tiếp không cải thiện |
| `lr0=0.01` | Learning rate ban đầu (tốc độ học của AI) |
| `mosaic=1.0` | Kỹ thuật augmentation — quan trọng cho vật nhỏ như găng tay |
| `project=runs/train` | Lưu kết quả vào thư mục `runs/train/` |
| `name=ppe_v1` | Tên của lần training này |

### Bước 4.1 — Chạy thử nhanh (5 phút) — BẮT BUỘC làm trước

Trước khi chạy 100 epoch, hãy chạy 5 epoch để đảm bảo không có lỗi:

```bash
# Từ thư mục gốc dự án
yolo detect train \
  data=data/dataset.yaml \
  model=yolov8s.pt \
  epochs=5 \
  imgsz=640 \
  batch=16 \
  project=runs/train \
  name=ppe_sanity
```

**Kết quả tốt** — bạn thấy các dòng như sau (số loss giảm dần):

```
Epoch    GPU_mem   box_loss   cls_loss   dfl_loss
  1/5      4.52G      1.823      2.341      1.234
  2/5      4.52G      1.654      2.102      1.187
  3/5      4.52G      1.521      1.987      1.143
  4/5      4.52G      1.445      1.876      1.098
  5/5      4.52G      1.389      1.801      1.067
```

Các cột `box_loss`, `cls_loss`, `dfl_loss` phải **đi xuống** qua các epoch. Nếu đi lên hoặc không thay đổi → có vấn đề với dataset (xem phần Xử Lý Lỗi).

**Nếu gặp lỗi đỏ** → đọc thông báo lỗi và xem phần [Xử Lý Lỗi Thường Gặp](#xử-lý-lỗi-thường-gặp) ở cuối tài liệu.

### Bước 4.2 — Chạy training đầy đủ (1–3 giờ)

```bash
yolo detect train \
  data=data/dataset.yaml \
  model=yolov8s.pt \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  patience=20 \
  lr0=0.01 \
  mosaic=1.0 \
  project=runs/train \
  name=ppe_v1
```

**Để terminal chạy, không đóng lại.** Quá trình training sẽ hiện tiến độ từng epoch.

Khi training xong, bạn sẽ thấy:

```
100 epochs completed in 1.823 hours.
Results saved to runs/train/ppe_v1/
Weights saved to runs/train/ppe_v1/weights/
```

### Bước 4.3 — Xem kết quả training được lưu ở đâu

```bash
ls runs/train/ppe_v1/
```

```
weights/          ← Chứa best.pt và last.pt
results.png       ← Biểu đồ loss và accuracy
confusion_matrix.png  ← Ma trận nhầm lẫn giữa các lớp
val_batch0_pred.jpg   ← Ảnh mẫu với dự đoán của mô hình
```

Mở `results.png` bằng trình xem ảnh. Biểu đồ tốt trông như thế này:

```
Loss (phải đi xuống):     Accuracy/mAP (phải đi lên):
   \                           /‾‾‾‾
    \                         /
     \___                ____/
```

---

## Phase 5 — Đánh Giá Kết Quả

### Bước 5.1 — Chạy đánh giá trên test set

Test set là tập ảnh mô hình **chưa từng thấy trong quá trình training**. Đây là bài kiểm tra thực sự.

```bash
yolo detect val \
  data=data/dataset.yaml \
  model=runs/train/ppe_v1/weights/best.pt \
  split=test
```

### Bước 5.2 — Đọc kết quả đánh giá

Output mẫu:

```
                 Class     Images  Instances    mAP50   mAP50-95
                   all       877       3241     0.812      0.612
                helmet       ...                0.891
       reflective_vest       ...                0.834
                gloves       ...                0.723
          safety_boots       ...                0.798
       safety_glasses       ...                0.654
```

**Các chỉ số cần xem:**

| Chỉ số | Ý nghĩa | Mục tiêu |
|---|---|---|
| `mAP50` (all) | Độ chính xác tổng thể | **≥ 0.75** |
| `mAP50` từng lớp | Độ chính xác từng loại PPE | **≥ 0.60** |

**Ví dụ đọc kết quả:**
- `mAP50 = 0.812` → mô hình phát hiện đúng 81.2% PPE → **Tốt, đạt mục tiêu**
- `gloves mAP50 = 0.45` → găng tay chỉ phát hiện đúng 45% → **Cần cải thiện** (xem Phase xử lý lỗi)

### Bước 5.3 — Xem confusion matrix

```bash
ls runs/val/exp/
# Mở file confusion_matrix.png
```

Confusion matrix cho thấy các lớp bị nhầm lẫn với nhau. Ví dụ nếu mô hình hay nhầm `gloves` thành `safety_glasses` thì ô tương ứng sẽ có số cao.

---

## Phase 6 — Tích Hợp Vào Backend

### Bước 6.1 — Copy file weights vào backend

```bash
# Từ thư mục gốc dự án
cp runs/train/ppe_v1/weights/best.pt backend/models_weights/best.pt
```

**Chỉ cần copy 1 file duy nhất. Không cần sửa code nào.**

### Bước 6.2 — Tại sao không cần sửa code?

Vì `backend/config.py` đã có sẵn:

```python
MODEL_PATH = os.getenv("MODEL_PATH", str(MODELS_DIR / "best.pt"))
```

Và `backend/services/cv_engine.py` đã có logic:

```python
# 1. Thử load best.pt (mô hình custom của chúng ta)
# 2. Nếu không có → thử yolov8n.pt (fallback)
# 3. Nếu vẫn không có → tự download yolov8n.pt
```

Khi bạn copy `best.pt` vào đúng chỗ, backend tự động dùng nó trong lần restart tiếp theo.

### Bước 6.3 — Khởi động lại backend

```bash
cd backend
uvicorn main:app --reload
```

Kiểm tra log khởi động. Bạn phải thấy:

```
INFO:services.cv_engine:Loading YOLO model from: /path/to/backend/models_weights/best.pt
INFO:services.cv_engine:Model warmup complete
INFO:services.cv_engine:CV Engine ready ✅
```

**Nếu vẫn thấy dòng này là chưa đúng:**
```
WARNING: Custom model not found at ... Trying fallback: yolov8n.pt
```
→ Kiểm tra lại đường dẫn copy ở Bước 6.1.

---

## Phase 7 — Kiểm Tra Trên Giao Diện

### Bước 7.1 — Khởi động đầy đủ

Mở **2 terminal riêng biệt**:

```bash
# Terminal 1 — Backend
cd /home/user/Desktop/safety-ppe-checker/backend
uvicorn main:app --reload
```

```bash
# Terminal 2 — Frontend
cd /home/user/Desktop/safety-ppe-checker/frontend
npm run dev
```

Mở trình duyệt vào: **http://localhost:5173**

### Bước 7.2 — Upload ảnh thử nghiệm

Tìm một ảnh công nhân đang mặc đầy đủ PPE (hoặc dùng ảnh trong `data/demo/`).

Upload ảnh lên giao diện.

**Kết quả mong đợi với mô hình đã train:**

```json
{
  "overall_pass": true,
  "items": {
    "helmet":          { "detected": true,  "confidence": 0.89 },
    "reflective_vest": { "detected": true,  "confidence": 0.82 },
    "gloves":          { "detected": true,  "confidence": 0.71 },
    "safety_boots":    { "detected": true,  "confidence": 0.79 },
    "safety_glasses":  { "detected": true,  "confidence": 0.66 }
  }
}
```

Giao diện sẽ hiển thị:
- ✅ Dấu tích xanh cho PPE được phát hiện
- ❌ Dấu X đỏ cho PPE còn thiếu
- Kết quả **PASS** hoặc **FAIL**
- Ảnh có bounding box xung quanh các vật thể được phát hiện

### Bước 7.3 — Kiểm tra chi tiết qua Swagger UI (tùy chọn)

Truy cập: **http://localhost:8000/docs**

1. Nhấn vào `POST /api/v1/check-ppe`
2. Nhấn **Try it out**
3. Upload ảnh
4. Nhấn **Execute**

Swagger hiển thị toàn bộ JSON response, bao gồm cả `debug_info` với danh sách tất cả vật thể được phát hiện và confidence score của từng cái.

### Bước 7.4 — Không cần thay đổi gì trên Frontend hay Backend

| Thành phần | Cần thay đổi? | Lý do |
|---|---|---|
| `frontend/` | ❌ Không | UI đọc JSON từ backend, không quan tâm model nào đang chạy |
| `backend/routers/check_ppe.py` | ❌ Không | Router chỉ gọi `engine.run()`, không biết về model |
| `backend/services/cv_engine.py` | ❌ Không | Đã có logic load `best.pt` tự động |
| `backend/config.py` | ❌ Không | `PPE_CLASS_MAP` đã mapping đủ tên lớp từ dataset |
| `backend/models_weights/best.pt` | ✅ Copy vào | File duy nhất cần thêm |

---

## Xử Lý Lỗi Thường Gặp

### Lỗi 1: `CUDA out of memory`

```
RuntimeError: CUDA out of memory. Tried to allocate ...
```

**Cách sửa:** Giảm `batch` size:

```bash
# Thay batch=16 thành batch=8
yolo detect train ... batch=8 ...

# Nếu vẫn lỗi, giảm tiếp
yolo detect train ... batch=4 ...
```

### Lỗi 2: Loss không giảm (loss tăng hoặc đứng yên)

**Nguyên nhân thường gặp:** CLASS_REMAP sai — nhãn bị gán nhầm lớp.

**Cách kiểm tra:**

```bash
# Lấy ngẫu nhiên 1 ảnh và file nhãn tương ứng
ls data/processed/train/images/ | head -1
# Ví dụ: construction-ppe_worker_001.jpg

# Xem file nhãn của ảnh đó
cat data/processed/train/labels/construction-ppe_worker_001.txt
# Các số đầu dòng chỉ được là 0,1,2,3,4
```

Nếu thấy số lớn hơn 4 (ví dụ `7 0.512 ...`) → CLASS_REMAP của bạn bị sai. Quay lại Phase 2 và sửa lại.

### Lỗi 3: `No such file or directory: data/processed/train/images`

Dataset chưa được gộp. Chạy lại Phase 2:

```bash
python scripts/prepare_dataset.py
```

### Lỗi 4: Mô hình chạy nhưng không phát hiện gì (all detected: false)

1. Kiểm tra log backend — xem dòng nào đang load:

```bash
# Trong log của uvicorn, tìm dòng:
INFO:services.cv_engine:Loading YOLO model from: ...
```

2. Nếu đang load `yolov8n.pt` thay vì `best.pt` → file copy sai chỗ:

```bash
ls backend/models_weights/
# Phải thấy best.pt ở đây
```

3. Kiểm tra `debug_info` trong response từ Swagger. Xem trường `raw_detections`:
   - Nếu `raw_detections = []` → mô hình không phát hiện gì cả (thường do ảnh quá tối, không có người)
   - Nếu có `raw_detections` nhưng `ppe_class = null` → tên lớp trong model không khớp với `PPE_CLASS_MAP` trong `config.py`

### Lỗi 5: mAP thấp dưới 0.60 sau khi train

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `gloves` hoặc `safety_glasses` mAP < 0.50 | Vật thể nhỏ, khó nhận diện ở 640px | Chạy lại với `imgsz=1280` |
| Tất cả lớp đều thấp | Không đủ data, training quá ít | Thêm `epochs=150`, dùng `yolov8m.pt` |
| val loss tăng khi train loss giảm | Overfitting — model học thuộc lòng | Thêm `dropout=0.1 weight_decay=0.0005` |
| Loss giảm rất chậm | Learning rate chưa phù hợp | Thêm `warmup_epochs=5 lr0=0.001` |

---

## Tóm Tắt: 6 Lệnh Bạn Sẽ Chạy

```bash
# 1. Cài thư viện
pip install ultralytics roboflow pyyaml

# 2. Tải Construction-PPE dataset
cd data/raw && python -c "from roboflow import Roboflow; rf=Roboflow(api_key='YOUR_KEY'); rf.workspace('construction-ppe').project('construction-ppe-detection').version(1).download('yolov8', location='construction-ppe')"

# 3. Tải SH17 dataset
python -c "from roboflow import Roboflow; rf=Roboflow(api_key='YOUR_KEY'); rf.workspace('roboflow-universe-projects').project('sh17-dataset').version(1).download('yolov8', location='sh17')"

# 4. Gộp và chuyển đổi nhãn (từ thư mục gốc dự án)
cd ../.. && python scripts/prepare_dataset.py

# 5. Train mô hình
yolo detect train data=data/dataset.yaml model=yolov8s.pt epochs=100 imgsz=640 batch=16 patience=20 lr0=0.01 mosaic=1.0 project=runs/train name=ppe_v1

# 6. Deploy: copy 1 file duy nhất vào backend
cp runs/train/ppe_v1/weights/best.pt backend/models_weights/best.pt
```

Sau bước 6, restart backend. Giao diện hoạt động ngay, không cần thay đổi gì thêm.

---

## Giải Thích Thuật Ngữ

**Fine-tuning (Tinh chỉnh):**
Lấy một mô hình đã được train sẵn trên dữ liệu lớn (COCO — 80 lớp, hàng triệu ảnh), rồi tiếp tục train thêm trên dữ liệu chuyên biệt (PPE — 5 lớp, ~8,000 ảnh). Mô hình giữ nguyên "kiến thức nền" và học thêm kiến thức mới. Nhanh hơn và chính xác hơn so với train từ đầu.

**mAP50 (Mean Average Precision at 50% IoU):**
Chỉ số đo độ chính xác tổng thể. Nếu mô hình vẽ khung quanh mũ bảo hộ và khung đó chồng lên ít nhất 50% với khung thực tế → tính là đúng. mAP là trung bình của precision trên tất cả các lớp. `mAP50 = 0.80` nghĩa là phát hiện đúng 80%. Mục tiêu của chúng ta: ≥ 0.75.

**Epoch:**
Một lần duyệt qua toàn bộ dataset training. 100 epochs nghĩa là AI xem mỗi ảnh 100 lần (mỗi lần theo thứ tự ngẫu nhiên khác nhau và có biến đổi ảnh nhỏ để tránh học thuộc lòng).

**best.pt:**
File lưu trọng số (weights) của mô hình tại thời điểm accuracy cao nhất trong quá trình training. Không nhất thiết là epoch cuối cùng. Luôn dùng `best.pt`, không dùng `last.pt`.

**Bounding box:**
Khung hình chữ nhật mà mô hình vẽ xung quanh vật thể phát hiện được. Trong file nhãn YOLO, được biểu diễn bằng 4 số: `center_x center_y width height` (tất cả từ 0.0 đến 1.0, là tỷ lệ so với kích thước ảnh).

**Confidence score:**
Độ tin cậy của mô hình về một phát hiện, từ 0.0 đến 1.0. Ví dụ `confidence: 0.89` nghĩa là mô hình 89% chắc chắn đây là mũ bảo hộ. Backend chỉ chấp nhận phát hiện có confidence vượt ngưỡng trong `config.py` (0.40–0.50 tùy lớp).

**CLASS_REMAP:**
Bảng chuyển đổi ID lớp từ dataset gốc sang ID tiêu chuẩn của dự án. Đây là bước dễ mắc lỗi nhất — nếu mapping sai, mô hình sẽ học nhầm (ví dụ nghĩ rằng "không có mũ" là "mũ bảo hộ").

**Singleton CVEngine:**
`cv_engine.py` chỉ load mô hình **một lần duy nhất** khi request đầu tiên đến. Các request sau dùng lại instance đó. Lý do: load model mất vài giây, không thể làm mỗi request.

---

*Tài liệu này được tạo cho dự án Safety PPE Checker — Sprint 1, tháng 3/2026.*
