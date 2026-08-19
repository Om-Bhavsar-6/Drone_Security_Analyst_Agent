from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.models.alert import SeverityLevel

class SearchRequest(BaseModel):
    query: Optional[str] = Field(default=None, description="FTS search query across descriptions, objects, locations")
    object_type: Optional[str] = Field(default=None, description="Filter by object type (e.g. vehicle, person)")
    location: Optional[str] = Field(default=None, description="Filter by specific location/zone")
    start_time: Optional[datetime] = Field(default=None, description="Filter start ISO timestamp")
    end_time: Optional[datetime] = Field(default=None, description="Filter end ISO timestamp")
    min_severity: Optional[SeverityLevel] = Field(default=None, description="Filter alerts with severity")
    limit: int = Field(default=20, ge=1, le=100)

class SearchResultItem(BaseModel):
    frame_id: str
    timestamp: datetime
    location: str
    description: str
    objects: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    risk_indicators: List[str]
    has_alert: bool = False
    alert_severity: Optional[str] = None
    rank_score: Optional[float] = None

class SearchResponse(BaseModel):
    query: Optional[str]
    total_matches: int
    results: List[SearchResultItem]

class ChatRequest(BaseModel):
    prompt: str = Field(description="Operational question for the Security Analyst Agent")
    session_id: Optional[str] = Field(default="default-session")

class ToolExecutionTrace(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result_summary: str

class ChatResponse(BaseModel):
    response: str
    intent: str
    tools_used: List[ToolExecutionTrace] = Field(default_factory=list)
    referenced_frames: List[str] = Field(default_factory=list)
    confidence: float = 0.95

class SummaryResponse(BaseModel):
    summary: str
    total_frames_analyzed: int
    total_events_tracked: int
    total_alerts_triggered: int
    critical_alerts_count: int
    key_observations: List[str]
