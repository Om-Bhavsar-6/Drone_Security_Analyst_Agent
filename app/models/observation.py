from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DetectedObject(BaseModel):
    object_type: str = Field(description="Categorical type: person, vehicle, animal, object")
    label: str = Field(description="Specific entity label: e.g., 'Ford F150', 'Individual'")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Visual attributes like color, clothing, etc.")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence score")

class DetectedActivity(BaseModel):
    activity_type: str = Field(description="Activity classification: loitering, entering, exiting, grazing, pacing, parking")
    confidence: float = Field(ge=0.0, le=1.0, description="Activity confidence score")
    notes: Optional[str] = Field(default=None)

class StructuredObservation(BaseModel):
    frame_id: str
    description: str = Field(description="Dense natural language narrative of the frame")
    objects: List[DetectedObject] = Field(default_factory=list)
    activities: List[DetectedActivity] = Field(default_factory=list)
    risk_indicators: List[str] = Field(default_factory=list, description="Extracted indicators: after_hours, face_obscured, fence_perimeter")
    vlm_confidence: float = Field(ge=0.0, le=1.0, default=0.9)
