"""
merge_roboflow.py — Import và merge data từ Roboflow vào processed_v2/

Chạy từ repo root:
    python scripts/merge_roboflow.py --source /path/to/roboflow_export --split train

Quy trình:
1. Đọc data từ thư mục Roboflow export (format YOLOv8)
2. Map class names về project standard (qua CLASS_REMAP)
3. Chỉ giữ images có gloves hoặc glasses (ưu tiên bổ sung 2 class yếu)
4. Copy sang data/processed_v2/ (không overwrite processed/)

Cấu trúc Roboflow export cần có:
    export_dir/
    ├── train/images/*.jpg
    ├── train/labels/*.txt
    ├── valid/images/*.jpg  (Roboflow dùng "valid" thay vì "val")
    ├── valid/labels/*.txt
    └── data.yaml           (class names của dataset nguồn)
"""

import argparse
import shutil
import sys
import yaml
from pathlib import Path
from collections import defaultdict

# Project-standard class IDs — phải khớp data/dataset.yaml
PROJECT_CLASSES = {
    "helmet": 0,
    "reflective_vest": 1,
    "gloves": 2,
    "safety_boots": 3,
    "safety_glasses": 4,
}

# Map từ tên class phổ biến trong các Roboflow datasets → project standard name
# Thêm vào đây khi gặp dataset mới có tên class khác
CLASS_REMAP = {
    # Helmet variants
    "helmet": "helmet",
    "hard hat": "helmet",
    "hardhat": "helmet",
    "hard-hat": "helmet",
    "Helmet": "helmet",
    "Hard Hat": "helmet",
    # Vest variants
    "vest": "reflective_vest",
    "reflective_vest": "reflective_vest",
    "safety vest": "reflective_vest",
    "safety-vest": "reflective_vest",
    "Safety-vest": "reflective_vest",
    "hi-vis": "reflective_vest",
    "high-vis vest": "reflective_vest",
    # Gloves variants
    "gloves": "gloves",
    "Gloves": "gloves",
    "work gloves": "gloves",
    "protective gloves": "gloves",
    "insulated gloves": "gloves",
    "safety gloves": "gloves",
    # Boots variants
    "boots": "safety_boots",
    "safety_boots": "safety_boots",
    "safety boots": "safety_boots",
    "shoes": "safety_boots",
    "Shoes": "safety_boots",
    "safety shoes": "safety_boots",
    # Glasses variants
    "safety_glasses": "safety_glasses",
    "safety glasses": "safety_glasses",
    "goggles": "safety_glasses",
    "safety goggles": "safety_glasses",
    "Glasses": "safety_glasses",
    "glasses": "safety_glasses",
    "eye protection": "safety_glasses",
    "face shield": "safety_glasses",
}

PRIORITY_CLASSES = {2, 4}  # gloves, safety_glasses — chỉ import images có những class này


def load_source_classes(source_dir: Path) -> dict[int, str]:
    """Đọc class names từ data.yaml của Roboflow export."""
    yaml_candidates = ["data.yaml", "dataset.yaml", "_annotations.yaml"]
    for name in yaml_candidates:
        yaml_path = source_dir / name
        if yaml_path.exists():
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            names = data.get("names", [])
            if isinstance(names, list):
                return {i: n for i, n in enumerate(names)}
            elif isinstance(names, dict):
                return {int(k): v for k, v in names.items()}
    print(f"  [WARN] Không tìm thấy data.yaml trong {source_dir}")
    return {}


def remap_label_line(line: str, source_classes: dict[int, str]) -> str | None:
    """
    Chuyển đổi một dòng label từ source class IDs sang project class IDs.
    Trả về None nếu class không được map (unknown class → bỏ qua annotation đó).
    """
    parts = line.strip().split()
    if not parts:
        return None

    src_class_id = int(parts[0])
    src_class_name = source_classes.get(src_class_id, "")

    # Map về project standard name
    project_name = CLASS_REMAP.get(src_class_name)
    if project_name is None:
        return None  # Class không được nhận diện → bỏ qua

    project_id = PROJECT_CLASSES[project_name]
    # Giữ nguyên bbox coordinates, chỉ thay class ID
    return f"{project_id} " + " ".join(parts[1:])


def process_label_file(
    label_path: Path,
    source_classes: dict[int, str],
) -> tuple[list[str], set[int]]:
    """
    Đọc và remap label file.
    Trả về (remapped_lines, project_class_ids_present).
    """
    remapped = []
    project_ids = set()

    with open(label_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            new_line = remap_label_line(line, source_classes)
            if new_line is not None:
                remapped.append(new_line)
                project_ids.add(int(new_line.split()[0]))

    return remapped, project_ids


def find_image(images_dir: Path, stem: str) -> Path | None:
    for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp",
                ".JPG", ".JPEG", ".PNG"]:
        p = images_dir / (stem + ext)
        if p.exists():
            return p
    return None


def merge_split(
    source_split_dir: Path,
    dest_split_dir: Path,
    source_classes: dict[int, str],
    priority_only: bool,
    dry_run: bool,
) -> dict:
    labels_dir = source_split_dir / "labels"
    images_dir = source_split_dir / "images"

    if not labels_dir.exists():
        print(f"  [SKIP] {labels_dir} không tồn tại")
        return {}

    stats = defaultdict(int)
    label_files = sorted(labels_dir.glob("*.txt"))
    stats["total"] = len(label_files)

    dest_labels = dest_split_dir / "labels"
    dest_images = dest_split_dir / "images"

    if not dry_run:
        dest_labels.mkdir(parents=True, exist_ok=True)
        dest_images.mkdir(parents=True, exist_ok=True)

    for label_path in label_files:
        remapped_lines, project_ids = process_label_file(label_path, source_classes)

        if not remapped_lines:
            stats["skipped_no_known_class"] += 1
            continue

        # Nếu priority_only: chỉ import images có gloves hoặc glasses
        if priority_only and not (project_ids & PRIORITY_CLASSES):
            stats["skipped_no_priority_class"] += 1
            continue

        img_path = find_image(images_dir, label_path.stem)
        if img_path is None:
            stats["skipped_no_image"] += 1
            continue

        # Kiểm tra conflict (file đã tồn tại ở dest)
        dest_label = dest_labels / label_path.name
        dest_image = dest_images / img_path.name
        if dest_label.exists():
            # Rename với prefix để tránh overwrite
            stem = label_path.stem + "_rf"
            dest_label = dest_labels / (stem + ".txt")
            dest_image = dest_images / (stem + img_path.suffix)

        if dry_run:
            classes_str = ", ".join(
                PROJECT_CLASSES_INV.get(i, str(i)) for i in sorted(project_ids)
            )
            print(f"  [DRY-RUN] {label_path.name} → classes: [{classes_str}]")
        else:
            with open(dest_label, "w") as f:
                f.write("\n".join(remapped_lines) + "\n")
            shutil.copy2(img_path, dest_image)

        stats["imported"] += 1
        for pid in project_ids:
            stats[f"class_{pid}"] += 1

    return stats


# Inverse map for display
PROJECT_CLASSES_INV = {v: k for k, v in PROJECT_CLASSES.items()}


def main():
    parser = argparse.ArgumentParser(description="Merge Roboflow dataset into processed_v2/")
    parser.add_argument("--source", required=True, help="Thư mục Roboflow export")
    parser.add_argument("--split", default="all", choices=["train", "val", "all"])
    parser.add_argument("--priority-only", action="store_true", default=True,
                        help="Chỉ import images có gloves hoặc safety_glasses (default: True)")
    parser.add_argument("--all-classes", action="store_true",
                        help="Import tất cả images (override --priority-only)")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ print, không copy files")
    args = parser.parse_args()

    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"[ERROR] Source dir không tồn tại: {source_dir}")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent
    dest_base = repo_root / "data" / "processed_v2"

    source_classes = load_source_classes(source_dir)
    if not source_classes:
        print("[ERROR] Không đọc được class names từ data.yaml")
        print("Kiểm tra file data.yaml trong thư mục Roboflow export")
        sys.exit(1)

    print(f"Source classes: {source_classes}")
    print(f"Destination: {dest_base}")

    priority_only = args.priority_only and not args.all_classes
    if priority_only:
        print("Mode: PRIORITY ONLY (chỉ import images có gloves hoặc safety_glasses)")
    else:
        print("Mode: ALL CLASSES")

    # Roboflow dùng "valid" thay vì "val"
    split_map = {"train": "train", "val": "valid"}
    if args.split == "all":
        splits_to_process = [("train", "train"), ("val", "valid")]
    else:
        splits_to_process = [(args.split, split_map[args.split])]

    total_imported = 0
    for dest_split, src_split in splits_to_process:
        src_split_dir = source_dir / src_split
        if not src_split_dir.exists():
            # Thử tên khác
            src_split_dir = source_dir / dest_split
        if not src_split_dir.exists():
            print(f"\n[SKIP] Không tìm thấy split '{src_split}' hoặc '{dest_split}' trong source")
            continue

        print(f"\n--- Merge split: {src_split} → processed_v2/{dest_split} ---")
        dest_split_dir = dest_base / dest_split
        stats = merge_split(src_split_dir, dest_split_dir, source_classes, priority_only, args.dry_run)

        if not stats:
            continue

        print(f"  Total labels found:          {stats['total']}")
        print(f"  Imported:                    {stats['imported']}")
        print(f"  Skipped (no known class):    {stats['skipped_no_known_class']}")
        print(f"  Skipped (no priority class): {stats['skipped_no_priority_class']}")
        print(f"  Skipped (image not found):   {stats['skipped_no_image']}")
        print(f"  Class breakdown of imported:")
        for class_id, name in PROJECT_CLASSES.items():
            count = stats.get(f"class_{class_id}", 0)
            if count:
                print(f"    [{class_id}] {name}: {count}")
        total_imported += stats["imported"]

    print(f"\n{'='*50}")
    print(f"Tổng đã import: {total_imported} images")
    if not args.dry_run and total_imported > 0:
        print(f"\nBước tiếp theo:")
        print(f"1. Merge processed/ + processed_v2/ → chạy: python scripts/build_dataset_v2.py")
        print(f"2. Train: yolo detect train data=data/dataset_v2.yaml model=yolov8s.pt ...")


if __name__ == "__main__":
    main()
