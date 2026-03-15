"""
Router: Stats — Dashboard Statistics

GET /api/v1/stats → Aggregated pass/fail stats + violation breakdown

Reference: TP-DSH-001
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.inspection_service import get_stats
from schemas.stats import StatsResponse

router = APIRouter(prefix="/api/v1", tags=["Stats"])


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get dashboard statistics",
    description="Returns total inspections, pass/fail counts, and violation breakdown by PPE class.",
)
async def dashboard_stats(db: Session = Depends(get_db)):
    return get_stats(db)
