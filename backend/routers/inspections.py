"""
Router: Inspections — History & Export

GET /api/v1/inspections          → Paginated history list
GET /api/v1/inspections/export   → CSV download
GET /api/v1/inspections/{id}     → Single inspection detail

Reference: TP-DSH-001
"""

import csv
import io
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from services.inspection_service import (
    get_inspections,
    get_inspection_by_id,
    export_inspections_csv,
)
from schemas.inspection import InspectionListResponse, InspectionDetail

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Inspections"])


@router.get(
    "/inspections",
    response_model=InspectionListResponse,
    summary="Get inspection history",
    description="Returns paginated list of past inspections, newest first.",
)
async def list_inspections(
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    inspections, total = get_inspections(db, limit=limit, offset=offset)
    return InspectionListResponse(
        inspections=inspections,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/inspections/export",
    summary="Export inspections as CSV",
    description="Download all inspection records as a CSV file.",
)
async def export_csv(db: Session = Depends(get_db)):
    data = export_inspections_csv(db)

    if not data:
        raise HTTPException(status_code=404, detail="No inspections to export.")

    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    # Return as downloadable file
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),  # BOM for Excel
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=ppe_inspections_export.csv"
        },
    )


@router.get(
    "/inspections/{inspection_id}",
    response_model=InspectionDetail,
    summary="Get single inspection",
    description="Returns full details of one inspection by ID.",
)
async def get_single_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    result = get_inspection_by_id(db, inspection_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Inspection {inspection_id} not found.",
        )
    return result
