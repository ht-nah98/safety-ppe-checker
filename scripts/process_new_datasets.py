"""
process_new_datasets.py — Xử lý 3 Roboflow datasets, remap classes, merge vào processed_v2/

Chạy từ repo root:
    python scripts/process_new_datasets.py [--dry-run]

Datasets:
    DS1: data/raw/ppe.v3i.yolov8          (nc=12, có glove+glasses+boots)
    DS2: data/raw/PPE-Detection-with-Gloves.v9i.yolov8 (nc=4, có Gloves)
    DS3: data/raw/PPE-gloves.v2i.yolov8   (nc=10, có Gloves+gozluk/glasses)

Output: data/processed_v2/{train,val,test}/{images,labels}/
"""

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path

# ── Project standard classes ─────────────────────────────────────────────────
PROJECT_CLASSES = {
    "helmet":          0,
    "reflective_vest": 1,
    "gloves":          2,
    "safety_boots":    3,
    "safety_glasses":  4,
}
PROJECT_CLASSES_INV = {v: k for k, v in PROJECT_CLASSES.items()}

# ── Per-dataset class remapping ───────────────────────────────────────────────
# None = drop this class (negative classes, person, mask, etc.)
DS1_REMAP = {
    # class_name (in data.yaml order) -> project_name or None
    "bare_arm":    None,
    "boot":        "safety_boots",
    "glasses":     "safety_glasses",
    "glove":       "gloves",
    "hard_hat":    "helmet",
    "mask":        None,
    "no_glove":    None,
    "no_hard_hat": None,
    "no_mask":     None,
    "no_vest":     None,
    "person":      None,
    "vest":        "reflective_vest",
}

DS2_REMAP = {
    "Gloves":  "gloves",
    "Vest":    "reflective_vest",
    "helmet":  "helmet",
    "person":  None,
}

DS3_REMAP = {
    "Gloves":       "gloves",
    "face_mask":    None,
    "face_nomask":  None,
    "gozluk":       "safety_glasses",   # Turkish for "goggles/glasses"
    "hand_glove":   "gloves",
    "hand_noglove": None,
    "head_helmet":  "helmet",
    "head_nohelmet":None,
    "person":       None,
    "vest":         "reflective_vest",
}

DATASETS = [
    {
        "name": "DS1_ppe.v3i",
        "src": "data/raw/ppe.v3i.yolov8",
        "remap": DS1_REMAP,
        "splits": {"train": "train", "val": "valid", "test": "test"},
    },
    {
        "name": "DS2_PPE-Gloves",
        "src": "data/raw/PPE-Detection-with-Gloves.v9i.yolov8",
        "remap": DS2_REMAP,
        "splits": {"train": "train", "val": "valid", "test": "test"},
    },
    {
        "name": "DS3_PPE-gloves-iit",
        "src": "data/raw/PPE-gloves.v2i.yolov8",
        "remap": DS3_REMAP,
        "splits": {"train": "train", "val": "valid"},
    },
]

# Priority: only import images that have at least one of these classes
PRIORITY_CLASSES = {"gloves", "safety_glasses"}


def build_id_map(remap: dict[str, str | None]) -> dict[int, int | None]:
    """Convert name-based remap → {src_class_id: dst_class_id | None}."""
    id_map = {}
    for i, (src_name, dst_name) in enumerate(remap.items()):
        if dst_name is None:
            id_map[i] = None
        else:
            id_map[i] = PROJECT_CLASSES[dst_name]
    return id_map


def remap_label(label_path: Path, id_map: dict[int, int | None]) -> tuple[list[str], set[int]]:
    """Read label file, remap class IDs. Returns (new_lines, project_ids_present)."""
    new_lines = []
    project_ids = set()
    try:
        with open(label_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                src_id = int(parts[0])
                dst_id = id_map.get(src_id)
                if dst_id is None:
                    continue  # drop this annotation
                new_lines.append(f"{dst_id} " + " ".join(parts[1:]))
                project_ids.add(dst_id)
    except Exception as e:
        print(f"    [WARN] {label_path}: {e}")
    return new_lines, project_ids


def find_image(images_dir: Path, stem: str) -> Path | None:
    for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp",
                ".JPG", ".JPEG", ".PNG", ".BMP"]:
        p = images_dir / (stem + ext)
        if p.exists():
            return p
    return None


def process_dataset(ds_cfg: dict, repo_root: Path, dest_base: Path, dry_run: bool) -> dict:
    src_root = repo_root / ds_cfg["src"]
    id_map = build_id_map(ds_cfg["remap"])
    ds_name = ds_cfg["name"]

    total_stats = defaultdict(int)

    for dest_split, src_split in ds_cfg["splits"].items():
        src_labels = src_root / src_split / "labels"
        src_images = src_root / src_split / "images"
        dst_labels = dest_base / dest_split / "labels"
        dst_images = dest_base / dest_split / "images"

        if not src_labels.exists():
            print(f"  [SKIP] {src_labels} not found")
            continue

        label_files = sorted(src_labels.glob("*.txt"))
        split_stats = defaultdict(int)
        split_stats["total"] = len(label_files)

        if not dry_run:
            dst_labels.mkdir(parents=True, exist_ok=True)
            dst_images.mkdir(parents=True, exist_ok=True)

        for label_path in label_files:
            new_lines, project_ids = remap_label(label_path, id_map)

            # Must have at least one valid annotation
            if not new_lines:
                split_stats["skipped_no_valid_ann"] += 1
                continue

            # Priority filter: must have gloves or safety_glasses
            has_priority = any(
                PROJECT_CLASSES_INV.get(pid) in PRIORITY_CLASSES
                for pid in project_ids
            )
            if not has_priority:
                split_stats["skipped_no_priority"] += 1
                continue

            img_path = find_image(src_images, label_path.stem)
            if img_path is None:
                split_stats["skipped_no_image"] += 1
                continue

            # Avoid filename conflicts with a dataset prefix
            safe_stem = f"{ds_name[:4]}_{label_path.stem}"
            dst_label = dst_labels / (safe_stem + ".txt")
            dst_image = dst_images / (safe_stem + img_path.suffix)

            if not dry_run:
                with open(dst_label, "w") as f:
                    f.write("\n".join(new_lines) + "\n")
                shutil.copy2(img_path, dst_image)

            split_stats["imported"] += 1
            for pid in project_ids:
                split_stats[f"class_{pid}"] += 1

        # Accumulate
        for k, v in split_stats.items():
            total_stats[k] += v

        print(f"  [{dest_split}] total={split_stats['total']}  "
              f"imported={split_stats['imported']}  "
              f"skip_no_priority={split_stats['skipped_no_priority']}  "
              f"skip_no_ann={split_stats['skipped_no_valid_ann']}")

    return total_stats


def count_annotations(labels_dir: Path) -> dict[int, int]:
    counts = defaultdict(int)
    if not labels_dir.exists():
        return counts
    for f in labels_dir.glob("*.txt"):
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    counts[int(line.split()[0])] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    dest_base = repo_root / "data" / "processed_v2"

    mode = "[DRY-RUN]" if args.dry_run else "[LIVE]"
    print(f"Processing 3 Roboflow datasets → data/processed_v2/ {mode}")
    print(f"Priority filter: only images with gloves OR safety_glasses\n")

    grand = defaultdict(int)
    for ds_cfg in DATASETS:
        src_path = repo_root / ds_cfg["src"]
        if not src_path.exists():
            print(f"\n[SKIP] {ds_cfg['src']} not found")
            continue
        print(f"\n{'─'*55}")
        print(f"  {ds_cfg['name']}")
        print(f"{'─'*55}")
        stats = process_dataset(ds_cfg, repo_root, dest_base, args.dry_run)
        for k, v in stats.items():
            grand[k] += v

    print(f"\n{'='*55}")
    print(f"  GRAND TOTAL")
    print(f"{'='*55}")
    print(f"  Total label files scanned: {grand['total']}")
    print(f"  Imported:                  {grand['imported']}")
    print(f"  Skipped (no priority):     {grand['skipped_no_priority']}")
    print(f"  Skipped (no valid ann):    {grand['skipped_no_valid_ann']}")
    print(f"  Skipped (no image):        {grand['skipped_no_image']}")

    if not args.dry_run:
        print(f"\n  Class distribution in processed_v2/train/:")
        counts = count_annotations(dest_base / "train" / "labels")
        total_ann = sum(counts.values()) or 1
        for cid, name in PROJECT_CLASSES.items():
            c = counts.get(cid, 0)
            bar = "█" * int(c / total_ann * 40)
            flag = " ← STILL LOW" if c < 500 else ""
            print(f"    [{cid}] {name:<20s}: {c:5d} ({c/total_ann*100:.1f}%) {bar}{flag}")

        print(f"\n  Next: python scripts/build_dataset_v2.py")


if __name__ == "__main__":
    main()
