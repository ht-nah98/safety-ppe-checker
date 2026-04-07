"""
filter_dataset.py — Quarantine isolated object images gây training bias

Chạy từ repo root:
    python scripts/filter_dataset.py [--dry-run] [--split train]

Options:
    --dry-run   Chỉ in ra sẽ move gì, không thực sự move files
    --split     Split để xử lý (train/val/test, default: train)

Logic:
    - Images chỉ có gloves (class 2) alone → quarantine
    - Images chỉ có safety_glasses (class 4) alone → quarantine
    - Images có gloves/glasses KÈM ≥1 class khác → GIỮ LẠI (in-context, tốt)
    - Tất cả images khác → GIỮ LẠI

Reversible: files được MOVE sang data/quarantine/, không bị xóa.
Để restore: python scripts/filter_dataset.py --restore
"""

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path

CLASS_NAMES = {
    0: "helmet",
    1: "reflective_vest",
    2: "gloves",
    3: "safety_boots",
    4: "safety_glasses",
}

# Classes cần kiểm tra isolation bias
PROBLEM_CLASSES = {2: "gloves", 4: "safety_glasses"}


def parse_label_file(label_path: Path) -> set[int]:
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
        print(f"  [WARN] {label_path}: {e}")
    return classes


def should_quarantine(classes: set[int]) -> tuple[bool, str]:
    """
    Trả về (should_quarantine, reason).
    Chỉ quarantine nếu image có ĐỘC NHẤT một class trong PROBLEM_CLASSES.
    """
    if len(classes) != 1:
        return False, ""
    sole_class = next(iter(classes))
    if sole_class in PROBLEM_CLASSES:
        return True, f"isolated_{PROBLEM_CLASSES[sole_class]}"
    return False, ""


def find_image_file(images_dir: Path, stem: str) -> Path | None:
    """Tìm file ảnh tương ứng với label (jpg/jpeg/png/bmp)."""
    for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        candidate = images_dir / (stem + ext)
        if candidate.exists():
            return candidate
        candidate = images_dir / (stem + ext.upper())
        if candidate.exists():
            return candidate
    return None


def process_split(
    split: str,
    processed_dir: Path,
    quarantine_dir: Path,
    dry_run: bool,
) -> dict:
    labels_dir = processed_dir / split / "labels"
    images_dir = processed_dir / split / "images"

    if not labels_dir.exists():
        print(f"  [SKIP] {labels_dir} không tồn tại")
        return {}

    label_files = sorted(labels_dir.glob("*.txt"))
    stats = defaultdict(int)
    stats["total"] = len(label_files)

    for label_path in label_files:
        classes = parse_label_file(label_path)
        do_quarantine, reason = should_quarantine(classes)

        if not do_quarantine:
            stats["kept"] += 1
            continue

        # Xác định destination
        dest_labels = quarantine_dir / split / reason / "labels"
        dest_images = quarantine_dir / split / reason / "images"

        # Tìm file ảnh
        img_path = find_image_file(images_dir, label_path.stem)

        if dry_run:
            print(f"  [DRY-RUN] Would move: {label_path.name} ({reason})")
            stats[f"quarantine_{reason}"] += 1
            stats["quarantined"] += 1
            continue

        # Tạo thư mục quarantine nếu chưa có
        dest_labels.mkdir(parents=True, exist_ok=True)
        dest_images.mkdir(parents=True, exist_ok=True)

        # Move label file
        shutil.move(str(label_path), dest_labels / label_path.name)
        stats[f"quarantine_{reason}"] += 1
        stats["quarantined"] += 1

        # Move image file nếu tìm thấy
        if img_path:
            shutil.move(str(img_path), dest_images / img_path.name)
        else:
            print(f"  [WARN] Không tìm thấy ảnh cho {label_path.stem}")

    stats["kept"] = stats["total"] - stats["quarantined"]
    return stats


def restore_split(split: str, processed_dir: Path, quarantine_dir: Path) -> None:
    """Restore tất cả files đã quarantine về processed."""
    quarantine_split = quarantine_dir / split
    if not quarantine_split.exists():
        print(f"  [SKIP] Không có quarantine data cho split '{split}'")
        return

    restored = 0
    for reason_dir in quarantine_split.iterdir():
        if not reason_dir.is_dir():
            continue
        for subdir in ["labels", "images"]:
            src_dir = reason_dir / subdir
            dst_dir = processed_dir / split / subdir
            if not src_dir.exists():
                continue
            dst_dir.mkdir(parents=True, exist_ok=True)
            for f in src_dir.iterdir():
                shutil.move(str(f), dst_dir / f.name)
                restored += 1

    print(f"  Restored {restored} files cho split '{split}'")


def main():
    parser = argparse.ArgumentParser(description="Filter isolated object images")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ print, không move files")
    parser.add_argument("--split", default="train", choices=["train", "val", "test", "all"])
    parser.add_argument("--restore", action="store_true", help="Restore files đã quarantine")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    processed_dir = repo_root / "data" / "processed"
    quarantine_dir = repo_root / "data" / "quarantine"

    if not processed_dir.exists():
        print(f"[ERROR] Không tìm thấy {processed_dir}")
        sys.exit(1)

    splits = ["train", "val", "test"] if args.split == "all" else [args.split]

    if args.restore:
        print(f"Restoring quarantined files → {processed_dir}")
        for split in splits:
            restore_split(split, processed_dir, quarantine_dir)
        print("Done. Chạy audit_dataset.py để verify.")
        return

    mode = "[DRY-RUN]" if args.dry_run else "[LIVE]"
    print(f"PPE Dataset Filter {mode}")
    print(f"Source:     {processed_dir}")
    print(f"Quarantine: {quarantine_dir}")

    for split in splits:
        print(f"\n--- Split: {split} ---")
        stats = process_split(split, processed_dir, quarantine_dir, args.dry_run)

        if not stats:
            continue

        total = stats["total"]
        quarantined = stats["quarantined"]
        kept = stats["kept"]
        gloves_q = stats.get("quarantine_isolated_gloves", 0)
        glasses_q = stats.get("quarantine_isolated_safety_glasses", 0)

        print(f"  Total:       {total}")
        print(f"  Kept:        {kept} ({kept/total*100:.1f}%)")
        print(f"  Quarantined: {quarantined} ({quarantined/total*100:.1f}%)")
        print(f"    ├─ isolated gloves:         {gloves_q}")
        print(f"    └─ isolated safety_glasses: {glasses_q}")

    if not args.dry_run:
        print(f"\n✓ Files đã move sang {quarantine_dir}")
        print("  Để restore: python scripts/filter_dataset.py --restore")
        print("  Tiếp theo:  python scripts/audit_dataset.py  (verify)")
    else:
        print("\n[DRY-RUN] Không có file nào bị move. Chạy lại không có --dry-run để thực hiện.")


if __name__ == "__main__":
    main()
