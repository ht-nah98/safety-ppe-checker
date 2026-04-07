"""
audit_dataset.py — Phân tích chất lượng dataset PPE

Chạy từ repo root:
    python scripts/audit_dataset.py

Mục đích: Phát hiện "isolated object" images (chỉ có gloves hoặc glasses,
không có người mặc PPE đầy đủ) — nguyên nhân chính gây training bias.
"""

import os
import sys
from collections import defaultdict
from pathlib import Path

# Class mapping — phải khớp với data/dataset.yaml
CLASS_NAMES = {
    0: "helmet",
    1: "reflective_vest",
    2: "gloves",
    3: "safety_boots",
    4: "safety_glasses",
}

GLOVES_ID = 2
GLASSES_ID = 4


def parse_label_file(label_path: Path) -> set[int]:
    """Đọc file label YOLO, trả về set các class IDs có trong ảnh."""
    classes = set()
    try:
        with open(label_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                class_id = int(line.split()[0])
                if class_id in CLASS_NAMES:
                    classes.add(class_id)
    except Exception as e:
        print(f"  [WARN] Không đọc được {label_path}: {e}")
    return classes


def categorize_image(classes: set[int]) -> str:
    """Phân loại image dựa trên số lượng PPE classes."""
    n = len(classes)
    if n == 0:
        return "empty"
    elif n == 1:
        return "isolated"
    elif n <= 3:
        return "partial"
    else:
        return "full_ppe"


def audit_split(labels_dir: Path, split_name: str) -> dict:
    """Audit một split (train/val/test)."""
    if not labels_dir.exists():
        print(f"  [SKIP] {labels_dir} không tồn tại")
        return {}

    label_files = list(labels_dir.glob("*.txt"))
    if not label_files:
        print(f"  [SKIP] Không có file .txt trong {labels_dir}")
        return {}

    stats = {
        "total": len(label_files),
        "categories": defaultdict(int),
        "isolated_by_class": defaultdict(int),
        "class_counts": defaultdict(int),
        "isolated_files": defaultdict(list),  # class_id -> [filenames]
    }

    for label_path in label_files:
        classes = parse_label_file(label_path)
        category = categorize_image(classes)
        stats["categories"][category] += 1

        for c in classes:
            stats["class_counts"][c] += 1

        if category == "isolated":
            for c in classes:
                stats["isolated_by_class"][c] += 1
                stats["isolated_files"][c].append(label_path.stem)

    return stats


def print_report(split_name: str, stats: dict) -> None:
    if not stats:
        return

    total = stats["total"]
    cats = stats["categories"]
    isolated_total = cats.get("isolated", 0)

    print(f"\n{'='*60}")
    print(f"  Split: {split_name.upper()}  ({total} images)")
    print(f"{'='*60}")

    print("\n[Phân loại images]")
    for cat in ["full_ppe", "partial", "isolated", "empty"]:
        count = cats.get(cat, 0)
        pct = count / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        label = {
            "full_ppe": "Full PPE (≥4 classes)",
            "partial":  "Partial  (2-3 classes)",
            "isolated": "Isolated (1 class)   ",
            "empty":    "Empty    (0 classes) ",
        }[cat]
        print(f"  {label}: {count:5d} ({pct:5.1f}%)  {bar}")

    print("\n[Annotation counts per class]")
    for class_id, name in CLASS_NAMES.items():
        count = stats["class_counts"].get(class_id, 0)
        iso = stats["isolated_by_class"].get(class_id, 0)
        iso_pct = iso / count * 100 if count else 0
        flag = " ⚠️  HIGH BIAS" if iso_pct > 30 else ""
        print(f"  [{class_id}] {name:20s}: {count:5d} total,  {iso:4d} isolated ({iso_pct:5.1f}%){flag}")

    # Highlight problem classes
    gloves_iso = stats["isolated_by_class"].get(GLOVES_ID, 0)
    glasses_iso = stats["isolated_by_class"].get(GLASSES_ID, 0)
    gloves_total = stats["class_counts"].get(GLOVES_ID, 1)
    glasses_total = stats["class_counts"].get(GLASSES_ID, 1)

    print("\n[Chẩn đoán Problem Classes]")
    print(f"  gloves isolated:         {gloves_iso:4d} / {gloves_total:4d} = {gloves_iso/gloves_total*100:.1f}%")
    print(f"  safety_glasses isolated: {glasses_iso:4d} / {glasses_total:4d} = {glasses_iso/glasses_total*100:.1f}%")

    if gloves_iso / gloves_total > 0.20:
        print("\n  ⚠️  KHUYẾN NGHỊ: Chạy filter_dataset.py để quarantine isolated gloves images")
    if glasses_iso / glasses_total > 0.20:
        print("  ⚠️  KHUYẾN NGHỊ: Chạy filter_dataset.py để quarantine isolated glasses images")


def main():
    repo_root = Path(__file__).parent.parent
    processed_dir = repo_root / "data" / "processed"

    if not processed_dir.exists():
        print(f"[ERROR] Không tìm thấy {processed_dir}")
        print("Hãy chạy script từ repo root: python scripts/audit_dataset.py")
        sys.exit(1)

    print("PPE Dataset Audit Report")
    print(f"Thư mục: {processed_dir}")

    all_stats = {}
    for split in ["train", "val", "test"]:
        labels_dir = processed_dir / split / "labels"
        stats = audit_split(labels_dir, split)
        if stats:
            all_stats[split] = stats
            print_report(split, stats)

    # Summary
    if "train" in all_stats:
        train = all_stats["train"]
        gloves_iso = train["isolated_by_class"].get(GLOVES_ID, 0)
        glasses_iso = train["isolated_by_class"].get(GLASSES_ID, 0)
        print(f"\n{'='*60}")
        print("  TỔNG KẾT")
        print(f"{'='*60}")
        print(f"  Isolated gloves images cần quarantine:  {gloves_iso}")
        print(f"  Isolated glasses images cần quarantine: {glasses_iso}")
        print(f"\n  Chạy tiếp: python scripts/filter_dataset.py")


if __name__ == "__main__":
    main()
