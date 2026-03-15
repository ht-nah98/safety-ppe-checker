"""
Inspection ORM Model — SQLAlchemy

Table: inspections
Stores every PPE check result with image paths and detection data.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text

from database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    overall_pass = Column(Boolean, nullable=False)
    image_path = Column(String, nullable=True)
    annotated_image_path = Column(String, nullable=True)
    results_json = Column(Text, nullable=False)  # JSON string of PPE items
    processing_time_ms = Column(Integer, nullable=True)

    def __repr__(self):
        status = "PASS" if self.overall_pass else "FAIL"
        return f"<Inspection {self.id[:8]}... {status} at {self.created_at}>"
