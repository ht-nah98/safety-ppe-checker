# DATA STRATEGY: Dataset cho PPE Detection

**Document**: DATA-STRATEGY.md
**Created**: 2026-03-15
**Status**: Finalized
**Purpose**: Phân tích và quyết định dataset nào dùng cho training YOLOv8 detect PPE

---

## 1. YÊU CẦU DỮ LIỆU CỦA PROJECT

Hệ thống cần detect **5 PPE classes bắt buộc**:

| Class (code) | Tên tiếng Việt | Ghi chú |
|-------------|----------------|---------|
| `helmet` | Mũ bảo hộ | Class quan trọng nhất, phổ biến nhất trong dataset |
| `reflective_vest` | Áo phản quang | Dễ detect nhờ màu sắc nổi bật |
| `gloves` | Găng tay bảo hộ | Nhỏ trong ảnh, khó detect nhất |
| `safety_boots` | Giày bảo hộ | Ở chân, cần ảnh toàn thân |
| `safety_glasses` | Kính bảo hộ | Nhỏ, hay bị miss |

**Tiêu chí chọn dataset:**
1. Có đủ cả 5 class trên (hoặc có thể map được)
2. Format YOLOv8 (hoặc dễ convert)
3. Đủ lớn cho training (≥ 1,000 ảnh)
4. License cho phép dùng cho demo/research

---

## 2. PHÂN TÍCH CÁC DATASET ĐÃ NGHIÊN CỨU

### Dataset 1: Construction-PPE (Ultralytics) ⭐ PRIMARY

**Nguồn:** Ultralytics official — `https://docs.ultralytics.com/datasets/detect/construction-ppe/`

| Thuộc tính | Chi tiết |
|-----------|---------|
| Số ảnh | 1,416 (1,132 train / 143 val / 141 test) |
| Số class | 11 classes |
| Format | YOLOv8 native (sẵn sàng dùng) |
| Size | 178.4 MB |
| License | AGPL-3.0 |

**11 Classes chi tiết:**

| Nhóm | Classes |
|------|---------|
| PPE có (Positive) | `helmet`, `gloves`, `vest`, `boots`, `goggles` |
| PPE thiếu (Negative) | `no_helmet`, `no_goggle`, `no_gloves`, `no_boots`, `none` |
| Khác | `Person` |

**Mapping vào project:**

| Class dataset | → | Class project |
|-------------|---|---------------|
| `helmet` | → | `helmet` ✅ |
| `vest` | → | `reflective_vest` ✅ |
| `gloves` | → | `gloves` ✅ |
| `boots` | → | `safety_boots` ✅ |
| `goggles` | → | `safety_glasses` ✅ |
| `no_helmet` | → | Tín hiệu FAIL cho helmet |
| `no_goggle` | → | Tín hiệu FAIL cho safety_glasses |
| `no_gloves` | → | Tín hiệu FAIL cho gloves |
| `no_boots` | → | Tín hiệu FAIL cho safety_boots |

**Điểm mạnh:**
- ✅ Có đủ cả 5 class cần thiết
- ✅ CÓ NEGATIVE CLASSES — dataset duy nhất trong danh sách có "no_helmet", "no_gloves"... Đây là lợi thế lớn nhất cho bài toán phát hiện vi phạm
- ✅ YOLOv8 native — không cần convert, `yolo train data=construction-ppe.yaml` là chạy được
- ✅ Tích hợp sẵn với Ultralytics, download tự động

**Điểm yếu:**
- ⚠️ Chỉ 1,416 ảnh — tương đối nhỏ, cần supplement
- ⚠️ License AGPL-3.0 — nếu commercialize phải open source code (OK cho demo)
- ⚠️ Ảnh từ công trường xây dựng quốc tế, không phải ngành điện lực VN

**Download:**
```bash
# Cách 1: Tự động khi train
yolo detect train data=construction-ppe.yaml model=yolov8n.pt epochs=100

# Cách 2: Download thủ công
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/construction-ppe.zip
unzip construction-ppe.zip -d data/raw/construction-ppe/
```

---

### Dataset 2: SH17 Dataset ⭐ SUPPLEMENT

**Nguồn:** GitHub — `https://github.com/ahmadmughees/SH17dataset`
**Kaggle:** `https://www.kaggle.com/datasets/mugheesahmad/sh17-dataset-for-ppe-detection`

| Thuộc tính | Chi tiết |
|-----------|---------|
| Số ảnh | 8,099 annotated images |
| Tổng objects | 75,994 instances |
| Số class | 17 classes |
| Format | Cần verify (likely YOLO hoặc COCO) |
| License | CC BY-NC-SA 4.0 (non-commercial OK) |

**17 Classes — mapping vào project:**

| Class SH17 | Map vào project | Ghi chú |
|-----------|-----------------|---------|
| `Helmet` | `helmet` ✅ | Direct map |
| `Safety-vest` | `reflective_vest` ✅ | Direct map |
| `Gloves` | `gloves` ✅ | Direct map |
| `Shoes` | `safety_boots` ⚠️ | Shoes bao gồm cả giày thường — cần lọc |
| `Glasses` | `safety_glasses` ⚠️ | Glasses bao gồm cả kính thường — cần lọc |
| `Person`, `Head`, `Face`, `Hands`, `Foot` | Bỏ qua | Không cần |
| `Face-mask-medical`, `Face-guard`, `Ear`, `Earmuffs`, `Tools`, `Medical-suit`, `Safety-suit` | Bỏ qua | Không liên quan |

**Benchmark trên SH17:**
- YOLOv9-e: **mAP50 = 70.9%**, mAP50-95 = 48.7%

**Điểm mạnh:**
- ✅ Lớn nhất trong danh sách (8,099 ảnh) — tăng diversity đáng kể
- ✅ Độ phân giải cao (max 8192×5462)
- ✅ Thu thập từ nhiều môi trường công nghiệp toàn cầu
- ✅ CC BY-NC-SA 4.0 — OK cho demo/research

**Điểm yếu:**
- ❌ KHÔNG có negative classes — không detect "thiếu PPE" trực tiếp
- ⚠️ `Shoes` và `Glasses` class quá rộng — có thể gây false positive

**Download:**
```bash
pip install kaggle
kaggle datasets download -d mugheesahmad/sh17-dataset-for-ppe-detection
unzip sh17-dataset-for-ppe-detection.zip -d data/raw/sh17/
```

---

### Dataset 3: PPE Dataset Mendeley 2025

**Nguồn:** `https://data.mendeley.com/datasets/zkzghjvpn2`

| Thuộc tính | Chi tiết |
|-----------|---------|
| Số ảnh | 2,286 (640×640 pixels) |
| Classes | Chỉ: helmets, reflective vests |
| Format | YOLOv8/YOLOv11 compatible |
| Size | 225 MB |
| License | CC BY 4.0 (**tự do nhất**) |

**Đánh giá:** Chỉ có 2/5 class cần thiết. Dùng để bổ sung nếu cần thêm ảnh helmet/vest, nhưng KHÔNG đủ dùng độc lập.

---

### Dataset 4: PPE_DATASET_COCO (Kaggle)

**Nguồn:** `https://www.kaggle.com/datasets/shlokraval/ppe-dataset`

| Thuộc tính | Chi tiết |
|-----------|---------|
| Số files | 44,000 files (2.54 GB) |
| Format | COCO JSON — cần convert sang YOLO |
| License | Apache 2.0 |

**Đánh giá:** Rất lớn nhưng format COCO cần thêm bước convert. Dùng nếu cần scale up sau khi có kết quả ban đầu từ Construction-PPE + SH17.

---

### Dataset 5: Safety Helmet Wearing Dataset (SHWD)

**Nguồn:** `https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset`

| Thuộc tính | Chi tiết |
|-----------|---------|
| Số ảnh | 7,581 |
| Classes | Chỉ 2: `helmet` (positive), `head` (negative = không đội mũ) |
| Format | VOC XML — cần convert |

**Đánh giá:** Chuyên sâu cho helmet, nhưng chỉ 1/5 class. Bổ sung nếu cần tăng accuracy riêng cho helmet detection.

---

## 3. SO SÁNH TỔNG QUAN

| Dataset | helmet | vest | gloves | boots | glasses | Negative | Images | Format | License | Dùng |
|---------|:------:|:----:|:------:|:-----:|:-------:|:--------:|-------:|--------|---------|:----:|
| Construction-PPE | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 1,416 | YOLOv8 | AGPL-3.0 | **PRIMARY** |
| SH17 | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | 8,099 | Verify | CC BY-NC-SA | **SUPPLEMENT** |
| Mendeley 2025 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | 2,286 | YOLOv8 | CC BY 4.0 | Optional |
| COCO PPE | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | 44,000 | COCO JSON | Apache 2.0 | Phase 2 |
| SHWD | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | 7,581 | VOC XML | MIT | Không cần |

---

## 4. QUYẾT ĐỊNH DATASET — CHIẾN LƯỢC

### Chiến lược: 2-tier approach

**TIER 1 — MVP Demo (Sprint 1):** Construction-PPE only

Lý do chọn làm bước đầu:
- Setup trong < 30 phút (YOLOv8 tự download)
- Có đủ cả 5 class ngay lập tức
- Có negative classes — detect cả vi phạm lẫn tuân thủ
- Đủ để prove concept cho demo

**TIER 2 — Tăng accuracy (Sprint 1 tuần 2):** Merge với SH17

Lý do merge thêm SH17:
- Tăng từ 1,416 → ~9,500 ảnh training
- Tăng diversity (nhiều môi trường, nhiều quốc gia)
- Tăng accuracy cho gloves và safety_glasses

---

### Cách sử dụng Negative Classes (Quan trọng)

**Vấn đề với detection approach thuần túy:**
- Nếu chỉ detect "có helmet" → không biết đang detect hay không detect
- Nếu không detect được do ảnh tối/mờ → sẽ nhầm là FAIL

**Giải pháp đề xuất — 2 cách:**

**Cách A: Chỉ detect positive classes (Đơn giản, dùng cho demo)**
```
Detect helmet, vest, gloves, boots, glasses
Nếu confidence ≥ threshold → detected = True → PASS cho item đó
Nếu không detect được → detected = False → FAIL cho item đó
```
- Ưu điểm: Đơn giản, dễ implement
- Nhược điểm: Nếu ảnh tối/mờ → false FAIL

**Cách B: Detect cả positive và negative classes (Chính xác hơn)**
```
Detect tất cả 11 class từ Construction-PPE
Nếu "helmet" detected → PASS
Nếu "no_helmet" detected → FAIL (chắc chắn hơn)
Nếu cả hai không detected → uncertain (cần ảnh tốt hơn)
```
- Ưu điểm: Phân biệt được "không detect" vs "thật sự vi phạm"
- Phù hợp hơn cho production

**Quyết định cho Demo:** Dùng **Cách A** (đơn giản) + thêm warning nếu confidence thấp

---

## 5. CLASS MAPPING CHÍNH THỨC

Bảng mapping từ tất cả datasets về 5 class chuẩn của project:

| Class project | Từ Construction-PPE | Từ SH17 | Từ Mendeley |
|--------------|---------------------|---------|-------------|
| `helmet` | `helmet` | `Helmet` | `helmet` |
| `reflective_vest` | `vest` | `Safety-vest` | `safety-vest` |
| `gloves` | `gloves` | `Gloves` | ❌ không có |
| `safety_boots` | `boots` | `Shoes` (⚠️ cẩn thận) | ❌ không có |
| `safety_glasses` | `goggles` | `Glasses` (⚠️ cẩn thận) | ❌ không có |

**Lưu ý khi merge SH17:**
- `Shoes` trong SH17 bao gồm giày thường → chỉ giữ lại ảnh có safety boots rõ ràng (qua visual inspection hoặc filter bằng context)
- `Glasses` trong SH17 bao gồm kính mắt thường → tương tự, cần lọc

---

## 6. KẾ HOẠCH DOWNLOAD & CHUẨN BỊ DATA

### Tuần 1 — Song song với viết docs

**Ngày 1–2: Download Construction-PPE**
```bash
# Tạo thư mục
mkdir -p projects/safety-ppe-checker/data/raw/construction-ppe

# Download (tự động khi train lần đầu)
cd projects/safety-ppe-checker
yolo detect train data=construction-ppe.yaml model=yolov8n.pt epochs=1
# → Dataset sẽ auto-download vào ~/.ultralytics/datasets/
```

**Ngày 3–4: Download SH17 (nếu cần)**
```bash
pip install kaggle
# Cần setup kaggle API key trước: https://www.kaggle.com/settings → API
kaggle datasets download -d mugheesahmad/sh17-dataset-for-ppe-detection
```

**Ngày 5: Chuẩn bị demo test images**
```
data/demo/
├── pass/        ← 5 ảnh đủ PPE, ánh sáng tốt
├── fail_helmet/ ← 3 ảnh thiếu mũ
├── fail_gloves/ ← 3 ảnh thiếu găng tay
├── fail_glasses/← 3 ảnh thiếu kính
├── fail_mixed/  ← 3 ảnh thiếu nhiều mục
└── edge_cases/  ← 3 ảnh ánh sáng kém / góc lạ
```

### Folder structure cho data
```
projects/safety-ppe-checker/
└── data/
    ├── raw/
    │   ├── construction-ppe/   ← Download từ Ultralytics
    │   └── sh17/               ← Download từ Kaggle (nếu cần)
    ├── processed/
    │   ├── images/
    │   │   ├── train/
    │   │   ├── val/
    │   │   └── test/
    │   └── labels/
    │       ├── train/
    │       ├── val/
    │       └── test/
    ├── demo/                   ← Test images cho demo presentation
    └── dataset.yaml            ← Config file cho YOLOv8 training
```

### File dataset.yaml cho project
```yaml
# dataset.yaml
path: ./data/processed
train: images/train
val:   images/val
test:  images/test

nc: 5  # number of classes
names:
  0: helmet
  1: reflective_vest
  2: gloves
  3: safety_boots
  4: safety_glasses
```

---

## 7. EXPECTED PERFORMANCE

Dựa trên benchmark của các dataset:

| Model | Dataset | mAP50 | Dự kiến với project |
|-------|---------|-------|---------------------|
| YOLOv8n | Construction-PPE only | ~65-70% | Đủ cho demo |
| YOLOv8n | Construction-PPE + SH17 | ~75-80% | Target của project |
| YOLOv9-e | SH17 only | 70.9% | Reference |

**Confidence thresholds theo class:**

| Class | Threshold | Lý do |
|-------|-----------|-------|
| `helmet` | 0.50 | Lớn, dễ detect |
| `reflective_vest` | 0.50 | Màu sắc nổi bật |
| `gloves` | 0.40 | Nhỏ trong ảnh |
| `safety_boots` | 0.45 | Ở chân, cần ảnh toàn thân |
| `safety_glasses` | 0.40 | Nhỏ, hay bị miss |

---

## 8. RISK & MITIGATION

| Risk | Xác suất | Mitigation |
|------|---------|------------|
| Construction-PPE quá nhỏ (1,416 ảnh), accuracy thấp | Medium | Merge SH17 ngay Sprint 1 tuần 2 |
| Gloves/glasses accuracy < 70% | High | Hạ threshold + note trong demo |
| SH17 Shoes/Glasses map sai | Medium | Visual inspection sample trước khi merge |
| Dataset ngành xây dựng khác ngành điện | Low | Fine-tune nếu có data thực từ công ty |
| Kaggle API setup mất thời gian | Low | Fallback: download trực tiếp từ website |

---

## 9. QUYẾT ĐỊNH CUỐI CÙNG

```
✅ PRIMARY:    Construction-PPE (Ultralytics) — BẮT BUỘC
✅ SUPPLEMENT: SH17 Dataset (Kaggle) — NÊN DÙNG
⬜ OPTIONAL:   Mendeley 2025 — chỉ nếu cần thêm helmet/vest
❌ SKIP:       SHWD — chỉ có helmet class
❌ PHASE 2:    COCO PPE — quá lớn, cần convert, để scale up sau
```

**Ưu tiên download:**
1. Construction-PPE (Sprint 1, Ngày 1 — tự động)
2. SH17 (Sprint 1, Ngày 2–3 — nếu accuracy chưa đạt target)

---

## 10. TÀI LIỆU THAM KHẢO

| Dataset | Link | License |
|---------|------|---------|
| Construction-PPE (Ultralytics) | https://docs.ultralytics.com/datasets/detect/construction-ppe/ | AGPL-3.0 |
| SH17 Dataset | https://github.com/ahmadmughees/SH17dataset | CC BY-NC-SA 4.0 |
| SH17 (Kaggle mirror) | https://www.kaggle.com/datasets/mugheesahmad/sh17-dataset-for-ppe-detection | CC BY-NC-SA 4.0 |
| Mendeley PPE 2025 | https://data.mendeley.com/datasets/zkzghjvpn2 | CC BY 4.0 |
| PPE COCO Dataset | https://www.kaggle.com/datasets/shlokraval/ppe-dataset | Apache 2.0 |
| SHWD | https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset | MIT |

---

> **Changelog**
> | Version | Date | Changes |
> |---------|------|---------|
> | v1.0 | 2026-03-15 | Initial data strategy — based on research from TA DOING PROJECT.txt |
