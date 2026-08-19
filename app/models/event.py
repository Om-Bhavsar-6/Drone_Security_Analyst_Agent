from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class TrackedEvent(BaseModel):
    event_id: str
    entity_key: str = Field(description="Unique fingerprint for entity across frames (e.g. vehicle:ford_f150:blue, person:hoodie:main_gate)")
    entity_type: str = Field(description="vehicle, person, unknown")
    label: str
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int = 1
    locations: List[str] = Field(default_factory=list)
    frame_ids: List[str] = Field(default_factory=list)
    activities_observed: List[str] = Field(default_factory=list)
    status: str = "active"  # active, completed, flagged
    notes: Optional[str] = None
