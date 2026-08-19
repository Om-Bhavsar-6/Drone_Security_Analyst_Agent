from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityAlert(BaseModel):
    alert_id: str
    timestamp: datetime
    frame_id: str
    location: str
    rule_id: str
    rule_name: str
    severity: SeverityLevel
    risk_score: float = Field(ge=0.0, le=1.0)
    detection_confidence: float = Field(ge=0.0, le=1.0)
    message: str
    recommended_action: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    acknowledged: bool = False
