from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.models.telemetry import Telemetry

class FramePacket(BaseModel):
    frame_id: str = Field(description="Unique idempotent frame identifier, e.g. FRM-20260818-0001")
    sequence_number: int = Field(ge=0, description="Monotonically increasing sequence number")
    timestamp: datetime = Field(description="Capture timestamp")
    telemetry: Telemetry = Field(description="Synchronized telemetry data")
    image_reference: Optional[str] = Field(default=None, description="Image URI, file path or base64 token")
    raw_frame_summary: Optional[str] = Field(default=None, description="Initial simulation annotation or source tag")
