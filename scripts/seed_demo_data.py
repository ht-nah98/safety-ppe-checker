"""
Seed Demo Data — Generate fake inspection records for dashboard demo.

Usage:
    cd backend
    python ../scripts/seed_demo_data.py

Creates 30 inspection records in the database with realistic distribution:
- ~65% PASS, ~35% FAIL
- FAIL scenarios vary across different PPE classes
"""

import json
import random
import uuid
import sys
import os
from datetime import datetime, timedelta, timezone

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import SessionLocal, create_tables
from models.inspection import Inspection
from config import REQUIRED_PPE_CLASSES


def generate_pass_result():
    """Generate a PASS result with all 5 items detected."""
    items = {}
    for cls in REQUIRED_PPE_CLASSES:
        items[cls] = {
            "detected": True,
            "confidence": round(random.uniform(0.70, 0.98), 2),
        }
    return items, True


def generate_fail_result():
    """Generate a FAIL result with 1-3 items missing."""
    items = {}
    # Decide how many items to miss (1-3)
    num_missing = random.choices([1, 2, 3], weights=[50, 35, 15])[0]

    # Gloves and glasses are most commonly missed
    miss_weights = {
        "helmet": 5,
        "reflective_vest": 10,
        "gloves": 40,
        "safety_boots": 15,
        "safety_glasses": 30,
    }
    missing_items = random.sample(
        REQUIRED_PPE_CLASSES,
        k=min(num_missing, len(REQUIRED_PPE_CLASSES)),
    )
    # Bias towards gloves/glasses
    if num_missing == 1:
        missing_items = random.choices(
            REQUIRED_PPE_CLASSES,
            weights=[miss_weights[c] for c in REQUIRED_PPE_CLASSES],
            k=1,
        )

    for cls in REQUIRED_PPE_CLASSES:
        if cls in missing_items:
            items[cls] = {"detected": False, "confidence": 0.0}
        else:
            items[cls] = {
                "detected": True,
                "confidence": round(random.uniform(0.65, 0.95), 2),
            }
    return items, False


def seed_data(num_records: int = 30):
    """Generate and insert seed data."""
    create_tables()
    db = SessionLocal()

    try:
        # Clear existing data (for re-seeding)
        existing = db.query(Inspection).count()
        if existing > 0:
            print(f"⚠️  Found {existing} existing records. Skipping seed.")
            print("   Delete ppe_checker.db first if you want to re-seed.")
            return

        now = datetime.now(timezone.utc)
        records = []

        for i in range(num_records):
            # ~65% PASS, ~35% FAIL
            is_pass = random.random() < 0.65
            if is_pass:
                items, overall_pass = generate_pass_result()
            else:
                items, overall_pass = generate_fail_result()

            # Spread records over past 7 days
            created_at = now - timedelta(
                days=random.randint(0, 6),
                hours=random.randint(6, 17),  # Working hours
                minutes=random.randint(0, 59),
            )

            inspection = Inspection(
                id=str(uuid.uuid4()),
                created_at=created_at,
                overall_pass=overall_pass,
                image_path=None,  # No actual images for seed data
                annotated_image_path=None,
                results_json=json.dumps(items),
                processing_time_ms=random.randint(800, 2500),
            )
            records.append(inspection)

        db.add_all(records)
        db.commit()

        pass_count = sum(1 for r in records if r.overall_pass)
        fail_count = len(records) - pass_count

        print(f"✅ Seeded {num_records} inspection records:")
        print(f"   PASS: {pass_count} ({pass_count/num_records*100:.0f}%)")
        print(f"   FAIL: {fail_count} ({fail_count/num_records*100:.0f}%)")
        print(f"   Date range: past 7 days")

    finally:
        db.close()


if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    seed_data(num)
