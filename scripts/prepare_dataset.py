"""
Merges Construction-PPE + SH17 datasets into data/processed/
with unified 5-class label IDs matching data/dataset.yaml.

Canonical class IDs:
    0: helmet
    1: reflective_vest
    2: gloves
    3: safety_boots
    4: safety_glasses

Usage (from repo root):
    python scripts/prepare_dataset.py

Prerequisites:
    - data/raw/construction-ppe/  (downloaded from Roboflow, YOLOv8 format)
    - data/raw/sh17/              (downloaded from Roboflow, YOLOv8 format)

Output:
    data/processed/
    ├── train/images/   ← merged train images
    ├── train/labels/   ← remapped train labels
    ├── val/images/
    ├── val/labels/
    ├── test/images/
    └── test/labels/
"""

import logging
import shutil
import sys
import yaml
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
OUT_DIR = REPO_ROOT / "data" / "processed"
SPLITS = ["train", "val", "test"]

# ---------------------------------------------------------------------------
# CLASS_REMAP: (dataset_name, original_class_id) → canonical_class_id
#
# IMPORTANT: These indices are derived from reading each dataset's data.yaml.
# Before running, verify with:
#   cat data/raw/construction-ppe/data.yaml
#   cat data/raw/sh17/data.yaml
#
# Construction-PPE typical class order (Roboflow export):
#   0: helmet        1: no_helmet   2: vest   3: no_vest
#   4: gloves        5: no_gloves   6: boots  7: glasses
#
# SH17 typical class order:
#   0: hard-hat      1: gloves      2: jacket       3: keyboard
#   4: laptop        5: person      6: phone        7: shoes
#   8: ear-protector 9: safety-vest 10: no-hardhat  11: no-safety-vest
#   12: no-gloves    13: ...
#   (exact indices vary — re-verify from data.yaml after download)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# CLASS_REMAP: (dataset_name, original_class_id) → canonical_class_id
#
# Target Canonical classes:
#   0: helmet
#   1: reflective_vest
#   2: gloves
#   3: safety_boots
#   4: safety_glasses
# ---------------------------------------------------------------------------
CLASS_REMAP: dict[tuple[str, int], int] = {
    # --- Construction-PPE ---
    ("construction-ppe", 0): 3,   # boots  → safety_boots
    ("construction-ppe", 1): 2,   # gloves → gloves
    ("construction-ppe", 2): 0,   # helmet → helmet
    ("construction-ppe", 4): 1,   # vest   → reflective_vest

    # --- SH17 ---
    ("sh17", 8): 4,               # glasses     → safety_glasses
    ("sh17", 9): 2,               # gloves      → gloves
    ("sh17", 10): 0,              # helmet      → helmet
    ("sh17", 14): 3,              # shoes       → safety_boots
    ("sh17", 16): 1,              # safety-vest → reflective_vest
}


def load_dataset_yaml(dataset_dir: Path) -> dict:
    """Load and return a dataset's data.yaml, or empty dict if missing."""
    yaml_candidates = list(dataset_dir.glob("*.yaml")) + list(dataset_dir.glob("*.yml"))
    if not yaml_candidates:
        return {}
    with open(yaml_candidates[0]) as f:
        return yaml.safe_load(f) or {}


def print_class_table(dataset_name: str, data: dict) -> None:
    """Log the class list from a dataset yaml for manual verification."""
    names = data.get("names", [])
    if isinstance(names, dict):
        items = sorted(names.items())
    elif names:
        items = list(enumerate(names))
    else:
        # Fallback for SH17 which lacks data.yaml
        if dataset_name == "sh17":
            items = [
                (8, "glasses"), (9, "gloves"), (10, "helmet"), (14, "shoes"), (16, "safety-vest")
            ]
        else:
            items = []

    logger.info("  %s classes:", dataset_name)
    for idx, name in items:
        mapped = CLASS_REMAP.get((dataset_name, int(idx)))
        status = f"→ canonical {mapped}" if mapped is not None else "  (skipped)"
        logger.info("    [%2d] %-25s %s", idx, name, status)


def remap_label_file(src: Path, dst: Path, dataset_name: str) -> bool:
    """
    Remap class IDs in a YOLO .txt label file.
    Returns True if the output file has at least one valid annotation.
    """
    lines_out: list[str] = []
    if not src.exists():
        return False
        
    with open(src) as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            orig_id = int(parts[0])
            new_id = CLASS_REMAP.get((dataset_name, orig_id))
            if new_id is not None:
                lines_out.append(f"{new_id} {' '.join(parts[1:])}")

    if lines_out:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, "w") as f:
            f.write("\n".join(lines_out) + "\n")
        return True
    return False


def process_dataset_roboflow(dataset_name: str, dataset_root: Path) -> dict[str, int]:
    """Process datasets with train/valid/test subdirectories (Construction-PPE)."""
    counts: dict[str, int] = {}
    roboflow_splits = {
        "train": "train",
        "val":   "valid",  # Roboflow usually uses 'valid'
        "test":  "test"
    }

    for target_split, source_split in roboflow_splits.items():
        img_src_dir = dataset_root / source_split / "images"
        lbl_src_dir = dataset_root / source_split / "labels"

        if not img_src_dir.exists():
            # Try flat source_split if images/ are not nested
            img_src_dir = dataset_root / source_split
            lbl_src_dir = dataset_root / source_split

        if not img_src_dir.exists():
            logger.warning("  No %s split found at %s", source_split, img_src_dir)
            counts[target_split] = 0
            continue

        img_dst_dir = OUT_DIR / target_split / "images"
        lbl_dst_dir = OUT_DIR / target_split / "labels"
        img_dst_dir.mkdir(parents=True, exist_ok=True)
        lbl_dst_dir.mkdir(parents=True, exist_ok=True)

        n_copied = 0
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

        for img_path in sorted(img_src_dir.iterdir()):
            if img_path.suffix.lower() not in image_extensions:
                continue

            lbl_path = lbl_src_dir / img_path.with_suffix(".txt").name
            unique_stem = f"{dataset_name}_{img_path.stem}"
            dst_lbl = lbl_dst_dir / f"{unique_stem}.txt"
            dst_img = img_dst_dir / f"{unique_stem}{img_path.suffix}"

            if remap_label_file(lbl_path, dst_lbl, dataset_name):
                shutil.copy2(img_path, dst_img)
                n_copied += 1

        counts[target_split] = n_copied
        logger.info("  %-20s %-5s → %d images", dataset_name, target_split, n_copied)

    return counts


def process_dataset_flat(dataset_name: str, dataset_root: Path) -> dict[str, int]:
    """Process flat datasets with file lists (SH17)."""
    counts: dict[str, int] = {}
    split_files = {
        "train": dataset_root / "train_files.txt",
        "val":   dataset_root / "val_files.txt",
    }
    
    img_src_dir = dataset_root / "images"
    lbl_src_dir = dataset_root / "labels"

    for split, list_file in split_files.items():
        if not list_file.exists():
            logger.warning("  Split list file %s not found", list_file)
            counts[split] = 0
            continue

        img_dst_dir = OUT_DIR / split / "images"
        lbl_dst_dir = OUT_DIR / split / "labels"
        img_dst_dir.mkdir(parents=True, exist_ok=True)
        lbl_dst_dir.mkdir(parents=True, exist_ok=True)

        n_copied = 0
        with open(list_file) as f:
            for line in f:
                img_name = line.strip()
                if not img_name:
                    continue
                
                img_path = img_src_dir / img_name
                lbl_path = lbl_src_dir / Path(img_name).with_suffix(".txt").name
                
                unique_stem = f"{dataset_name}_{Path(img_name).stem}"
                dst_lbl = lbl_dst_dir / f"{unique_stem}.txt"
                dst_img = img_dst_dir / f"{unique_stem}{img_path.suffix}"

                if remap_label_file(lbl_path, dst_lbl, dataset_name):
                    if img_path.exists():
                        shutil.copy2(img_path, dst_img)
                        n_copied += 1

        counts[split] = n_copied
        logger.info("  %-20s %-5s → %d images", dataset_name, split, n_copied)
    
    counts["test"] = 0 # SH17 didn't specify test split in text files
    return counts


def validate_output() -> bool:
    """Check for label files containing class IDs outside 0–4."""
    logger.info("\nValidating output labels...")
    bad_files: list[Path] = []
    for lbl_file in OUT_DIR.rglob("*.txt"):
        with open(lbl_file) as f:
            for i, line in enumerate(f, 1):
                parts = line.strip().split()
                if not parts:
                    continue
                try:
                    cls_id = int(parts[0])
                    if cls_id < 0 or cls_id > 4:
                        bad_files.append(lbl_file)
                        logger.error("  Bad class ID %d in %s (line %d)", cls_id, lbl_file, i)
                        break
                except ValueError:
                    continue
    if bad_files:
        logger.error("Validation FAILED: %d files with out-of-range class IDs", len(bad_files))
        return False
    logger.info("Validation PASSED — all class IDs in [0, 4]")
    return True


def print_summary(all_counts: dict[str, dict[str, int]]) -> None:
    logger.info("\n=== Dataset merge summary ===")
    totals: dict[str, int] = {s: 0 for s in SPLITS}
    for ds_name, counts in all_counts.items():
        for split, n in counts.items():
            totals[split] += n
    for split in SPLITS:
        logger.info("  %-5s total: %d images", split, totals[split])
    if totals["train"] < 1000:
        logger.warning(
            "Training set has fewer than 1000 images. "
            "Model quality may be limited — consider adding more data."
        )


def main() -> int:
    # Clear previous output to avoid stale data
    if OUT_DIR.exists():
        logger.info("\nRemoving existing data/processed/ ...")
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    # Process each dataset
    logger.info("\n=== Processing datasets ===")
    all_counts: dict[str, dict[str, int]] = {}
    
    # 1. Construction-PPE (Roboflow structure)
    cp_path = RAW_DIR / "construction-ppe"
    if cp_path.exists():
        logger.info("Processing: construction-ppe")
        all_counts["construction-ppe"] = process_dataset_roboflow("construction-ppe", cp_path)
    
    # 2. SH17 (Flat structure)
    sh_path = RAW_DIR / "sh17"
    if sh_path.exists():
        logger.info("Processing: sh17")
        all_counts["sh17"] = process_dataset_flat("sh17", sh_path)

    if not all_counts:
        logger.error("No datasets found in data/raw/")
        return 1

    print_summary(all_counts)
    ok = validate_output()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
