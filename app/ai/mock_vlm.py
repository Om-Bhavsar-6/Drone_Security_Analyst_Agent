import re
from typing import List, Dict, Any
from app.ai.base import BaseVLMEngine
from app.models.frame import FramePacket
from app.models.observation import StructuredObservation, DetectedObject, DetectedActivity
from app.core.logging import logger

class MockVLMEngine(BaseVLMEngine):
    """
    Deterministic, high-fidelity Mock VLM engine that inspects raw simulation cues
    or timestamps to produce richly structured security observations.
    """

    def analyze_frame(self, frame: FramePacket) -> StructuredObservation:
        desc_hint = (frame.raw_frame_summary or "").lower()
        hour = frame.timestamp.hour
        is_night = hour >= 22 or hour <= 5
        location = frame.telemetry.location_tag

        objects: List[DetectedObject] = []
        activities: List[DetectedActivity] = []
        risk_indicators: List[str] = []
        description = frame.raw_frame_summary or "Surveillance sweep in progress."

        # Scenario 1: Person / Loitering / Pacing
        if "hoodie" in desc_hint or "person" in desc_hint or "individual" in desc_hint or "loitering" in desc_hint:
            objects.append(
                DetectedObject(
                    object_type="person",
                    label="Adult Individual",
                    attributes={"clothing": "dark hoodie", "stance": "standing/pacing"},
                    confidence=0.94
                )
            )
            activity_type = "loitering" if "loitering" in desc_hint or "pacing" in desc_hint else "walking"
            activities.append(
                DetectedActivity(
                    activity_type=activity_type,
                    confidence=0.91,
                    notes=f"Observed near {location} perimeter"
                )
            )
            if is_night:
                risk_indicators.extend(["after_hours", "hooded_garment", "restricted_perimeter"])
            else:
                risk_indicators.append("perimeter_presence")

        # Scenario 2: Blue Ford F150 Truck
        elif "f150" in desc_hint or "truck" in desc_hint or "pickup" in desc_hint:
            objects.append(
                DetectedObject(
                    object_type="vehicle",
                    label="Ford F150",
                    attributes={"color": "blue", "type": "pickup truck"},
                    confidence=0.96
                )
            )
            if "backing" in desc_hint or "garage" in desc_hint or "entering" in desc_hint:
                activities.append(
                    DetectedActivity(
                        activity_type="entering",
                        confidence=0.93,
                        notes=f"Maneuvering into loading bay at {location}"
                    )
                )
                risk_indicators.append("vehicle_loading_access")
            elif "exiting" in desc_hint or "gate" in desc_hint:
                activities.append(
                    DetectedActivity(
                        activity_type="exiting",
                        confidence=0.95,
                        notes=f"Egressing property through {location}"
                    )
                )
                risk_indicators.append("vehicle_egress")
            else:
                activities.append(
                    DetectedActivity(
                        activity_type="parked",
                        confidence=0.90,
                        notes=f"Stationary at {location}"
                    )
                )

        # Scenario 3: Wildlife / Animals
        elif "deer" in desc_hint or "animal" in desc_hint:
            objects.append(
                DetectedObject(
                    object_type="animal",
                    label="Deer",
                    attributes={"species": "White-tailed deer", "count": 1},
                    confidence=0.92
                )
            )
            activities.append(
                DetectedActivity(
                    activity_type="grazing",
                    confidence=0.88,
                    notes="Harmless wildlife near tree line"
                )
            )
            risk_indicators.append("wildlife_non_threat")

        # Default fallback observation
        else:
            description = f"Clear surveillance aerial capture over {location}. No anomalous activities detected."
            activities.append(
                DetectedActivity(
                    activity_type="nominal_patrol",
                    confidence=0.98,
                    notes="Property clear"
                )
            )

        observation = StructuredObservation(
            frame_id=frame.frame_id,
            description=description,
            objects=objects,
            activities=activities,
            risk_indicators=risk_indicators,
            vlm_confidence=0.94
        )
        logger.debug(f"Mock VLM generated observation for {frame.frame_id}: {len(objects)} objects, {len(activities)} activities.")
        return observation
