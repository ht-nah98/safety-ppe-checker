"""
Inspection Service — Business Logic Layer

Handles:
- Saving inspection results to database
- Querying inspection history (with pagination)
- Computing stats aggregation
- CSV export
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models.inspection import Inspection
from config import REQUIRED_PPE_CLASSES, PPE_LABELS

logger = logging.getLogger(__name__)


def save_inspection(
    db: Session,
    inspection_id: str,
    cv_result: dict,
) -> Inspection:
    """
    Persist an inspection result to the database.

    Args:
        db: SQLAlchemy session
        inspection_id: UUID string
        cv_result: dict from CVEngine.run()
    """
    inspection = Inspection(
        id=inspection_id,
        created_at=datetime.now(timezone.utc),
        overall_pass=cv_result["overall_pass"],
        image_path=cv_result.get("original_image_path"),
        annotated_image_path=cv_result.get("annotated_image_path"),
        results_json=json.dumps(cv_result["items"]),
        processing_time_ms=cv_result.get("processing_time_ms"),
    )

    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    logger.info(f"Saved inspection {inspection_id[:8]} to DB")
    return inspection


def get_inspections(
    db: Session,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """
    Get paginated list of inspections, newest first.

    Returns: (list_of_inspection_dicts, total_count)
    """
    total = db.query(func.count(Inspection.id)).scalar()

    rows = (
        db.query(Inspection)
        .order_by(desc(Inspection.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    inspections = []
    for row in rows:
        items = json.loads(row.results_json)
        inspections.append({
            "id": row.id,
            "created_at": row.created_at,
            "overall_pass": row.overall_pass,
            "annotated_image_url": (
                f"/static/results/{row.id}_annotated.jpg"
                if row.annotated_image_path
                else None
            ),
            "processing_time_ms": row.processing_time_ms,
            "items": items,
        })

    return inspections, total


def get_inspection_by_id(db: Session, inspection_id: str) -> Optional[dict]:
    """Get single inspection by ID."""
    row = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not row:
        return None

    items = json.loads(row.results_json)
    return {
        "id": row.id,
        "created_at": row.created_at,
        "overall_pass": row.overall_pass,
        "annotated_image_url": (
            f"/static/results/{row.id}_annotated.jpg"
            if row.annotated_image_path
            else None
        ),
        "processing_time_ms": row.processing_time_ms,
        "items": items,
    }


def get_stats(db: Session) -> dict:
    """
    Compute aggregated statistics for the dashboard.

    Returns dict with:
      - total_inspections, pass_count, fail_count, pass_rate
      - violations_by_class: list sorted by count DESC
    """
    total = db.query(func.count(Inspection.id)).scalar() or 0
    pass_count = (
        db.query(func.count(Inspection.id))
        .filter(Inspection.overall_pass == True)
        .scalar()
        or 0
    )
    fail_count = total - pass_count
    pass_rate = round((pass_count / total * 100), 1) if total > 0 else 0.0

    # Count violations per PPE class
    # We need to parse results_json for failed inspections
    failed_rows = (
        db.query(Inspection.results_json)
        .filter(Inspection.overall_pass == False)
        .all()
    )

    violation_counts = {cls: 0 for cls in REQUIRED_PPE_CLASSES}
    for (results_json_str,) in failed_rows:
        items = json.loads(results_json_str)
        for cls_name, result in items.items():
            if cls_name in violation_counts and not result.get("detected", False):
                violation_counts[cls_name] += 1

    violations_by_class = []
    for cls_name, count in sorted(
        violation_counts.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = round((count / fail_count * 100), 1) if fail_count > 0 else 0.0
        violations_by_class.append({
            "class_name": cls_name,
            "label": PPE_LABELS.get(cls_name, cls_name),
            "count": count,
            "percentage": percentage,
        })

    return {
        "total_inspections": total,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": pass_rate,
        "violations_by_class": violations_by_class,
    }


def export_inspections_csv(db: Session) -> list[dict]:
    """
    Export all inspections as flat dicts for CSV generation.
    Returns list of dicts with columns ready for CSV writer.
    """
    rows = (
        db.query(Inspection)
        .order_by(desc(Inspection.created_at))
        .all()
    )

    export_data = []
    for row in rows:
        items = json.loads(row.results_json)

        flat = {
            "inspection_id": row.id,
            "timestamp": row.created_at.isoformat() if row.created_at else "",
            "overall_result": "PASS" if row.overall_pass else "FAIL",
            "processing_time_ms": row.processing_time_ms or 0,
        }

        # Add columns for each PPE class
        for cls in REQUIRED_PPE_CLASSES:
            item = items.get(cls, {})
            flat[f"{cls}_detected"] = item.get("detected", False)
            flat[f"{cls}_confidence"] = item.get("confidence", 0.0)

        # Violated items summary
        violated = [
            PPE_LABELS.get(k, k)
            for k, v in items.items()
            if not v.get("detected", False)
        ]
        flat["violated_items"] = ", ".join(violated) if violated else ""

        export_data.append(flat)

    return export_data
