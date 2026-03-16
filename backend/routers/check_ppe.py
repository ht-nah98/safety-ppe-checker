"""
Router: POST /api/v1/check-ppe

Main endpoint for PPE compliance checking.
Receives image → runs CV inference → saves result → returns JSON.

Reference: TP-CV-001 Section 2.1
"""

import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.cv_engine import CVEngine
from services.inspection_service import save_inspection
from schemas.inspection import InspectionResponse
from config import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE_BYTES, MODEL_PATH

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["PPE Check"])

# Singleton CV Engine — initialized once when this module loads
_engine: CVEngine = None


def get_engine() -> CVEngine:
    """Lazy initialization of CV Engine singleton."""
    global _engine
    if _engine is None:
        logger.info("Initializing CV Engine (first request)...")
        _engine = CVEngine(model_path=MODEL_PATH)
    return _engine


@router.post(
    "/check-ppe",
    response_model=InspectionResponse,
    summary="Check PPE compliance from image",
    description="Upload a photo of a worker. AI will detect 5 PPE items and return PASS/FAIL.",
)
async def check_ppe(
    image: UploadFile = File(..., description="Worker photo (JPEG/PNG, max 10MB)"),
    db: Session = Depends(get_db),
):
    # ── 1. Validate file type ──
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only JPEG and PNG accepted.",
        )

    # ── 2. Read and validate size ──
    image_bytes = await image.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB.",
        )

    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file received.",
        )

    # ── 3. Run CV inference ──
    inspection_id = str(uuid.uuid4())
    engine = get_engine()

    try:
        result = engine.run(image_bytes, inspection_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal inference error. Please try again.",
        )

    # ── 4. Save to database ──
    try:
        save_inspection(db, inspection_id, result)
    except Exception as e:
        logger.error(f"DB save error: {e}", exc_info=True)
        # Still return result even if DB fails (better UX for demo)

    # ── 5. Return response ──
    return InspectionResponse(
        inspection_id=inspection_id,
        overall_pass=result["overall_pass"],
        processing_time_ms=result["processing_time_ms"],
        annotated_image_url=f"/static/results/{inspection_id}_annotated.jpg",
        items=result["items"],
        created_at=datetime.now(timezone.utc),
        debug_info=result.get("debug_info"),
    )
