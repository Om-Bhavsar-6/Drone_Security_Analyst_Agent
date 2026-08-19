import uuid
from datetime import datetime
from typing import List, Optional
from app.models.frame import FramePacket
from app.models.observation import StructuredObservation, DetectedObject
from app.models.event import TrackedEvent
from app.storage.repositories import EventRepository
from app.core.logging import logger

class EventTracker:
    """
    Stateful cross-frame entity tracker.
    Maintains unified temporal events when entities (vehicles, individuals) appear across multiple frames.
    """
    def __init__(self, event_repo: Optional[EventRepository] = None):
        self.event_repo = event_repo or EventRepository()

    def _generate_entity_key(self, obj: DetectedObject, location: str) -> str:
        label_norm = obj.label.lower().replace(" ", "_")
        obj_type = obj.object_type.lower()
        color = str(obj.attributes.get("color", "")).lower()
        clothing = str(obj.attributes.get("clothing", "")).lower()
        
        if obj_type == "vehicle":
            return f"vehicle:{label_norm}:{color}"
        elif obj_type == "person":
            return f"person:{label_norm}:{clothing}"
        else:
            return f"{obj_type}:{label_norm}"

    def process_frame_observations(self, frame: FramePacket, observation: StructuredObservation) -> List[TrackedEvent]:
        updated_events: List[TrackedEvent] = []

        for obj in observation.objects:
            entity_key = self._generate_entity_key(obj, frame.telemetry.location_tag)
            existing_event = self.event_repo.get_event_by_key(entity_key)

            activities = [a.activity_type for a in observation.activities]
            location = frame.telemetry.location_tag

            if existing_event:
                # Update existing tracked event
                existing_event.last_seen = frame.timestamp
                existing_event.occurrence_count += 1
                if location not in existing_event.locations:
                    existing_event.locations.append(location)
                if frame.frame_id not in existing_event.frame_ids:
                    existing_event.frame_ids.append(frame.frame_id)
                for act in activities:
                    if act not in existing_event.activities_observed:
                        existing_event.activities_observed.append(act)
                
                existing_event.notes = f"Observed {existing_event.occurrence_count} times. Most recently at {location}."
                self.event_repo.save_or_update_event(existing_event)
                updated_events.append(existing_event)
                logger.info(f"Cross-Frame Entity Updated: {existing_event.label} seen {existing_event.occurrence_count} times across {existing_event.locations}")
            else:
                # Create brand new tracked event
                new_event = TrackedEvent(
                    event_id=f"EVT-{uuid.uuid4().hex[:8].upper()}",
                    entity_key=entity_key,
                    entity_type=obj.object_type,
                    label=f"{obj.label} ({obj.attributes.get('color') or obj.attributes.get('clothing') or 'unspecified'})",
                    first_seen=frame.timestamp,
                    last_seen=frame.timestamp,
                    occurrence_count=1,
                    locations=[location],
                    frame_ids=[frame.frame_id],
                    activities_observed=activities,
                    status="active",
                    notes=f"First spotted at {location}."
                )
                self.event_repo.save_or_update_event(new_event)
                updated_events.append(new_event)
                logger.info(f"New Entity Profiled: {new_event.label} at {location}")

        return updated_events
