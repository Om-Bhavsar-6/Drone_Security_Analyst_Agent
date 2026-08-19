from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Telemetry(BaseModel):
    drone_id: str = Field(default="DRONE-01", description="Identifier of the drone")
    timestamp: datetime = Field(description="ISO timestamp of telemetry record")
    latitude: float = Field(ge=-90.0, le=90.0, description="GPS Latitude in degrees")
    longitude: float = Field(ge=-180.0, le=180.0, description="GPS Longitude in degrees")
    altitude: float = Field(ge=0.0, description="Altitude above ground level in meters")
    location_tag: str = Field(description="Designated property zone or checkpoint")
    battery_percentage: Optional[float] = Field(default=95.0, ge=0.0, le=100.0)
    heading_degrees: Optional[float] = Field(default=0.0, ge=0.0, le=360.0)
    speed_mps: Optional[float] = Field(default=0.0, ge=0.0)
