"""
build_dataset_v2.py — Gộp processed/ (đã filter) + processed_v2/ (data mới) thành dataset_v2/

Chạy từ repo root:
    python scripts/build_dataset_v2.py [--dry-run]

Quy trình:
1. Copy toàn bộ data/processed/ (đã quarantine isolated images) → data/dataset_v2/
2. Append data/processed_v2/ (data mới từ Roboflow) → data/dataset_v2/
3. In class distribution cuối cùng để verify balance

Không xóa processed/ hay processed_v2/ — chỉ tạo dataset_v2/ mới.
"""

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path

CLASS_NAMES = {0: "helmet", 1: "reflective_vest", 2: "gloves", 3: "safety_boots", 4: "safety_glasses"}


def count_annotations(labels_dir: Path) -> dict[int, int]:
    counts = defaultdict(int)
    if not labels_dir.exists():
        return counts
    for label_file in labels_dir.glob("*.txt"):
        with open(label_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    counts[int(line.split()[0])] += 1
    return counts


def copy_split(src_split: Path, dst_split: Path, dry_run: bool) -> tuple[int, int]:
    """Copy images + labels từ src → dst. Trả về (images_copied, labels_copied)."""
    imgs_copied = 0
    lbls_copied = 0

    for subdir in ["images", "labels"]:
        src_dir = src_split / subdir
        dst_dir = dst_split / subdir
        if not src_dir.exists():
            continue
        if not dry_run:
            dst_dir.mkdir(parents=True, exist_ok=True)

        for f in src_dir.iterdir():
            dst_file = dst_dir / f.name
            # Nếu conflict, thêm suffix
            if dst_file.exists():
                dst_file = dst_dir / (f.stem + "_v2" + f.suffix)

            if not dry_run:
                shutil.copy2(f, dst_file)

            if subdir == "images":
                imgs_copied += 1
            else:
                lbls_copied += 1

    return imgs_copied, lbls_copied


def main():
    parser = argparse.ArgumentParser(description="Build merged dataset_v2 for retraining")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    processed_dir = repo_root / "data" / "processed"
    processed_v2_dir = repo_root / "data" / "processed_v2"
    dataset_v2_dir = repo_root / "data" / "dataset_v2"

    if not processed_dir.exists():
        print(f"[ERROR] {processed_dir} không tồn tại. Hãy chạy filter_dataset.py trước.")
        sys.exit(1)

    mode = "[DRY-RUN]" if args.dry_run else "[LIVE]"
    print(f"Build Dataset v2 {mode}")
    print(f"  Source 1 (cleaned): {processed_dir}")
    print(f"  Source 2 (new):     {processed_v2_dir}")
    print(f"  Destination:        {dataset_v2_dir}")

    splits = ["train", "val", "test"]
    grand_total_imgs = 0
    grand_total_lbls = 0

    for split in splits:
        print(f"\n--- Split: {split} ---")
        total_imgs = 0
        total_lbls = 0

        # Source 1: cleaned processed/
        src1 = processed_dir / split
        if src1.exists():
            imgs, lbls = copy_split(src1, dataset_v2_dir / split, args.dry_run)
            total_imgs += imgs
            total_lbls += lbls
            print(f"  From processed/:    {imgs} images, {lbls} labels")

        # Source 2: new data from Roboflow
        src2 = processed_v2_dir / split
        if src2.exists():
            imgs, lbls = copy_split(src2, dataset_v2_dir / split, args.dry_run)
            total_imgs += imgs
            total_lbls += lbls
            print(f"  From processed_v2/: {imgs} images, {lbls} labels")
        else:
            print(f"  From processed_v2/: (không có data mới cho split '{split}')")

        print(f"  Total: {total_imgs} images, {total_lbls} labels")
        grand_total_imgs += total_imgs
        grand_total_lbls += total_lbls

    # Class distribution report
    print(f"\n{'='*55}")
    print(f"  TỔNG: {grand_total_imgs} images, {grand_total_lbls} label files")

    if not args.dry_run:
        print("\n  Class distribution trong dataset_v2/train:")
        train_labels = dataset_v2_dir / "train" / "labels"
        counts = count_annotations(train_labels)
        total_ann = sum(counts.values())
        for class_id, name in CLASS_NAMES.items():
            count = counts.get(class_id, 0)
            pct = count / total_ann * 100 if total_ann else 0
            bar = "█" * int(pct / 2)
            flag = " ← cần thêm data" if count < 2000 else ""
            print(f"    [{class_id}] {name:20s}: {count:6d} ({pct:.1f}%) {bar}{flag}")

        print(f"\n  Dataset v2 sẵn sàng tại: {dataset_v2_dir}")
        print(f"\n  Bước tiếp theo — Train model v2:")
        print(f"  yolo detect train \\")
        print(f"    data=data/dataset_v2.yaml \\")
        print(f"    model=yolov8s.pt \\")
        print(f"    epochs=150 imgsz=1280 batch=8 \\")
        print(f"    copy_paste=0.3 mosaic=1.0 \\")
        print(f"    name=ppe_v2")


if __name__ == "__main__":
    main()
