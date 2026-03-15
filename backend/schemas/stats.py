"""
Pydantic Schemas — Stats Response
"""

from pydantic import BaseModel, Field
from typing import Dict


class PPEViolationStat(BaseModel):
    """Violation count for a single PPE class."""
    class_name: str
    label: str
    count: int
    percentage: float


class StatsResponse(BaseModel):
    """Response from GET /api/v1/stats"""
    total_inspections: int = Field(description="Total number of inspections")
    pass_count: int = Field(description="Number of PASS results")
    fail_count: int = Field(description="Number of FAIL results")
    pass_rate: float = Field(description="Pass rate as percentage (0-100)")
    violations_by_class: list[PPEViolationStat] = Field(
        description="Violation breakdown by PPE class, sorted by count descending"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_inspections": 50,
                    "pass_count": 35,
                    "fail_count": 15,
                    "pass_rate": 70.0,
                    "violations_by_class": [
                        {"class_name": "gloves", "label": "Găng tay bảo hộ", "count": 12, "percentage": 80.0},
                        {"class_name": "safety_glasses", "label": "Kính bảo hộ", "count": 9, "percentage": 60.0},
                    ]
                }
            ]
        }
    }
