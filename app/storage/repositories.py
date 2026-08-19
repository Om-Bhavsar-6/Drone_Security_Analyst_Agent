import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from app.storage.database import db, Database
from app.models.frame import FramePacket
from app.models.telemetry import Telemetry
from app.models.observation import StructuredObservation, DetectedObject, DetectedActivity
from app.models.alert import SecurityAlert, SeverityLevel
from app.models.event import TrackedEvent
from app.models.query import SearchResultItem
from app.core.logging import logger

class FrameRepository:
    def __init__(self, database: Database = db):
        self.database = database

    def save_frame_and_telemetry(self, frame: FramePacket) -> bool:
        """Idempotently saves frame and synchronized telemetry data."""
        with self.database.get_connection() as conn:
            # Check if frame already exists (Idempotency)
            existing = conn.execute("SELECT frame_id FROM frames WHERE frame_id = ?", (frame.frame_id,)).fetchone()
            if existing:
                logger.debug(f"Frame {frame.frame_id} already exists. Skipping insertion.")
                return False

            conn.execute(
                """
                INSERT INTO frames (frame_id, drone_id, sequence_number, timestamp, location_tag, image_reference)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    frame.frame_id,
                    frame.telemetry.drone_id,
                    frame.sequence_number,
                    frame.timestamp.isoformat(),
                    frame.telemetry.location_tag,
                    frame.image_reference,
                )
            )

            conn.execute(
                """
                INSERT INTO telemetry (frame_id, drone_id, timestamp, latitude, longitude, altitude, location_tag, battery_percentage, heading_degrees, speed_mps)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    frame.frame_id,
                    frame.telemetry.drone_id,
                    frame.telemetry.timestamp.isoformat(),
                    frame.telemetry.latitude,
                    frame.telemetry.longitude,
                    frame.telemetry.altitude,
                    frame.telemetry.location_tag,
                    frame.telemetry.battery_percentage,
                    frame.telemetry.heading_degrees,
                    frame.telemetry.speed_mps,
                )
            )
            conn.commit()
            return True

    def get_frame(self, frame_id: str) -> Optional[Dict[str, Any]]:
        with self.database.get_connection() as conn:
            row = conn.execute(
                """
                SELECT f.*, t.latitude, t.longitude, t.altitude, t.battery_percentage,
                       o.description, o.objects_json, o.activities_json, o.risk_indicators_json, o.vlm_confidence
                FROM frames f
                LEFT JOIN telemetry t ON f.frame_id = t.frame_id
                LEFT JOIN observations o ON f.frame_id = o.frame_id
                WHERE f.frame_id = ?
                """,
                (frame_id,)
            ).fetchone()
            if not row:
                return None
            
            d = dict(row)
            if d.get("objects_json"):
                d["objects"] = json.loads(d["objects_json"])
            if d.get("activities_json"):
                d["activities"] = json.loads(d["activities_json"])
            if d.get("risk_indicators_json"):
                d["risk_indicators"] = json.loads(d["risk_indicators_json"])
            return d

    def get_all_frames(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self.database.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT f.*, t.latitude, t.longitude, t.altitude,
                       o.description, o.objects_json, o.activities_json, o.risk_indicators_json, o.vlm_confidence,
                       a.alert_id, a.severity as alert_severity, a.message as alert_message
                FROM frames f
                LEFT JOIN telemetry t ON f.frame_id = t.frame_id
                LEFT JOIN observations o ON f.frame_id = o.frame_id
                LEFT JOIN alerts a ON f.frame_id = a.frame_id
                ORDER BY f.timestamp ASC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()
            
            result = []
            for row in rows:
                d = dict(row)
                d["objects"] = json.loads(d["objects_json"]) if d.get("objects_json") else []
                d["activities"] = json.loads(d["activities_json"]) if d.get("activities_json") else []
                d["risk_indicators"] = json.loads(d["risk_indicators_json"]) if d.get("risk_indicators_json") else []
                result.append(d)
            return result

    def get_frame_count(self) -> int:
        with self.database.get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM frames").fetchone()[0]


class ObservationRepository:
    def __init__(self, database: Database = db):
        self.database = database

    def save_observation(self, observation: StructuredObservation, location: str):
        objects_data = [obj.model_dump() for obj in observation.objects]
        activities_data = [act.model_dump() for act in observation.activities]
        
        objects_text = " ".join([f"{o.label} {o.object_type} {' '.join(str(v) for v in o.attributes.values())}" for o in observation.objects])
        activities_text = " ".join([f"{a.activity_type} {a.notes or ''}" for a in observation.activities])

        with self.database.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO observations (frame_id, description, objects_json, activities_json, risk_indicators_json, vlm_confidence)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    observation.frame_id,
                    observation.description,
                    json.dumps(objects_data),
                    json.dumps(activities_data),
                    json.dumps(observation.risk_indicators),
                    observation.vlm_confidence,
                )
            )

            # Insert into SQLite FTS5 Index
            conn.execute(
                """
                INSERT INTO fts_frames (frame_id, location, description, objects_text, activities_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    observation.frame_id,
                    location,
                    observation.description,
                    objects_text,
                    activities_text,
                )
            )
            conn.commit()


class AlertRepository:
    def __init__(self, database: Database = db):
        self.database = database

    def save_alert(self, alert: SecurityAlert):
        with self.database.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO alerts (alert_id, frame_id, timestamp, location, rule_id, rule_name, severity, risk_score, detection_confidence, message, recommended_action, metadata_json, acknowledged)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert.alert_id,
                    alert.frame_id,
                    alert.timestamp.isoformat(),
                    alert.location,
                    alert.rule_id,
                    alert.rule_name,
                    alert.severity.value,
                    alert.risk_score,
                    alert.detection_confidence,
                    alert.message,
                    alert.recommended_action,
                    json.dumps(alert.metadata),
                    1 if alert.acknowledged else 0,
                )
            )
            conn.commit()

    def get_all_alerts(self, min_severity: Optional[str] = None) -> List[Dict[str, Any]]:
        severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        with self.database.get_connection() as conn:
            if min_severity and min_severity.upper() in severity_order:
                min_idx = severity_order.index(min_severity.upper())
                allowed_severities = severity_order[min_idx:]
                placeholders = ",".join(["?"] * len(allowed_severities))
                rows = conn.execute(
                    f"SELECT * FROM alerts WHERE severity IN ({placeholders}) ORDER BY timestamp DESC",
                    allowed_severities
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM alerts ORDER BY timestamp DESC").fetchall()
            
            alerts = []
            for r in rows:
                d = dict(r)
                d["metadata"] = json.loads(d["metadata_json"]) if d.get("metadata_json") else {}
                d["acknowledged"] = bool(d["acknowledged"])
                alerts.append(d)
            return alerts

    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        with self.database.get_connection() as conn:
            row = conn.execute("SELECT * FROM alerts WHERE alert_id = ?", (alert_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            d["metadata"] = json.loads(d["metadata_json"]) if d.get("metadata_json") else {}
            d["acknowledged"] = bool(d["acknowledged"])
            return d

    def get_alert_count(self) -> int:
        with self.database.get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]


class EventRepository:
    def __init__(self, database: Database = db):
        self.database = database

    def get_event_by_key(self, entity_key: str) -> Optional[TrackedEvent]:
        with self.database.get_connection() as conn:
            row = conn.execute("SELECT * FROM events WHERE entity_key = ?", (entity_key,)).fetchone()
            if not row:
                return None
            return TrackedEvent(
                event_id=row["event_id"],
                entity_key=row["entity_key"],
                entity_type=row["entity_type"],
                label=row["label"],
                first_seen=datetime.fromisoformat(row["first_seen"]),
                last_seen=datetime.fromisoformat(row["last_seen"]),
                occurrence_count=row["occurrence_count"],
                locations=json.loads(row["locations_json"]),
                frame_ids=json.loads(row["frame_ids_json"]),
                activities_observed=json.loads(row["activities_json"]),
                status=row["status"],
                notes=row["notes"]
            )

    def save_or_update_event(self, event: TrackedEvent):
        with self.database.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO events (event_id, entity_key, entity_type, label, first_seen, last_seen, occurrence_count, locations_json, frame_ids_json, activities_json, status, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(event_id) DO UPDATE SET
                    last_seen = excluded.last_seen,
                    occurrence_count = excluded.occurrence_count,
                    locations_json = excluded.locations_json,
                    frame_ids_json = excluded.frame_ids_json,
                    activities_json = excluded.activities_json,
                    status = excluded.status,
                    notes = excluded.notes,
                    updated_at = datetime('now')
                """,
                (
                    event.event_id,
                    event.entity_key,
                    event.entity_type,
                    event.label,
                    event.first_seen.isoformat(),
                    event.last_seen.isoformat(),
                    event.occurrence_count,
                    json.dumps(event.locations),
                    json.dumps(event.frame_ids),
                    json.dumps(event.activities_observed),
                    event.status,
                    event.notes,
                )
            )
            conn.commit()

    def get_all_events(self) -> List[TrackedEvent]:
        with self.database.get_connection() as conn:
            rows = conn.execute("SELECT * FROM events ORDER BY last_seen DESC").fetchall()
            events = []
            for row in rows:
                events.append(
                    TrackedEvent(
                        event_id=row["event_id"],
                        entity_key=row["entity_key"],
                        entity_type=row["entity_type"],
                        label=row["label"],
                        first_seen=datetime.fromisoformat(row["first_seen"]),
                        last_seen=datetime.fromisoformat(row["last_seen"]),
                        occurrence_count=row["occurrence_count"],
                        locations=json.loads(row["locations_json"]),
                        frame_ids=json.loads(row["frame_ids_json"]),
                        activities_observed=json.loads(row["activities_json"]),
                        status=row["status"],
                        notes=row["notes"]
                    )
                )
            return events
