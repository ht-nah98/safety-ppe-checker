"""
Pydantic Schemas — Inspection Request/Response

Defines the API contract for PPE check results.
Matches: TP-CV-001 Section 2.1
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class PPEItemResult(BaseModel):
    """Result for a single PPE item."""
    detected: bool = Field(description="Whether this PPE item was detected")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Detection confidence score (0.0 to 1.0)"
    )


class DebugInfo(BaseModel):
    """Raw detection debug data — for development visibility."""
    model_path: str
    inference_conf_threshold: float
    raw_detections_count: int
    raw_detections: List[Dict[str, Any]]
    original_size: List[int]
    processed_size: List[int]
    mapping_logs: Optional[List[str]] = None

    model_config = {"protected_namespaces": ()}


class InspectionResponse(BaseModel):
    """Response from POST /api/v1/check-ppe"""
    inspection_id: str = Field(description="Unique inspection UUID")
    overall_pass: bool = Field(description="True only if ALL 5 PPE items detected")
    processing_time_ms: int = Field(description="Inference time in milliseconds")
    annotated_image_url: str = Field(description="URL to annotated image with bounding boxes")
    items: Dict[str, PPEItemResult] = Field(
        description="Detection result for each of the 5 PPE classes"
    )
    created_at: Optional[datetime] = None
    debug_info: Optional[DebugInfo] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "inspection_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "overall_pass": False,
                    "processing_time_ms": 1240,
                    "annotated_image_url": "/static/results/3fa85f64_annotated.jpg",
                    "items": {
                        "helmet":          {"detected": True,  "confidence": 0.94},
                        "reflective_vest": {"detected": True,  "confidence": 0.89},
                        "gloves":          {"detected": False, "confidence": 0.0},
                        "safety_boots":    {"detected": True,  "confidence": 0.76},
                        "safety_glasses":  {"detected": False, "confidence": 0.0},
                    }
                }
            ]
        }
    }


class InspectionDetail(BaseModel):
    """Full inspection record from database."""
    id: str
    created_at: datetime
    overall_pass: bool
    annotated_image_url: Optional[str] = None
    processing_time_ms: Optional[int] = None
    items: Dict[str, PPEItemResult]


class InspectionListResponse(BaseModel):
    """Paginated list of inspections."""
    inspections: list[InspectionDetail]
    total: int
    limit: int
    offset: int
