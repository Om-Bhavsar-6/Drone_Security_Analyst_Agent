import time
from typing import Dict, Any, Optional
from app.models.frame import FramePacket
from app.models.observation import StructuredObservation
from app.pipeline.synchronizer import IngestionSynchronizer
from app.storage.repositories import FrameRepository, ObservationRepository, AlertRepository, EventRepository
from app.ai.vlm_engine import vlm_engine
from app.detection.event_tracker import EventTracker
from app.detection.rules import rule_engine
from app.core.logging import logger

class FrameProcessor:
    def __init__(
        self,
        frame_repo: Optional[FrameRepository] = None,
        obs_repo: Optional[ObservationRepository] = None,
        alert_repo: Optional[AlertRepository] = None,
        event_repo: Optional[EventRepository] = None
    ):
        self.frame_repo = frame_repo or FrameRepository()
        self.obs_repo = obs_repo or ObservationRepository()
        self.alert_repo = alert_repo or AlertRepository()
        self.event_repo = event_repo or EventRepository()
        self.event_tracker = EventTracker(self.event_repo)

    def process_frame(self, frame: FramePacket) -> Dict[str, Any]:
        t0 = time.perf_counter()
        
        # 1. Validation & Synchronization
        valid, err = IngestionSynchronizer.validate_and_sync(frame)
        if not valid:
            logger.error(f"Ingestion validation failed for frame {frame.frame_id}: {err}")
            return {"status": "error", "error": err, "frame_id": frame.frame_id}

        # 2. Idempotent Storage of Frame & Telemetry
        is_new = self.frame_repo.save_frame_and_telemetry(frame)
        if not is_new:
            return {"status": "skipped", "message": "Duplicate frame rejected (Idempotent)", "frame_id": frame.frame_id}

        # 3. Multimodal VLM Inference
        t_vlm_start = time.perf_counter()
        observation = vlm_engine.analyze_frame(frame)
        t_vlm_ms = round((time.perf_counter() - t_vlm_start) * 1000, 2)

        # 3.5 Optional OpenCV Optical Rendering & HUD Overlay
        try:
            from app.pipeline.cv_utils import drone_cv_renderer
            drone_cv_renderer.generate_and_annotate_frame(frame, observation)
        except Exception as cv_err:
            logger.debug(f"OpenCV rendering note: {cv_err}")

        # 4. FTS5 Indexing and Observation Storage
        t_idx_start = time.perf_counter()
        self.obs_repo.save_observation(observation, location=frame.telemetry.location_tag)
        t_idx_ms = round((time.perf_counter() - t_idx_start) * 1000, 2)

        # 5. Cross-Frame Entity State Tracking
        tracked_events = self.event_tracker.process_frame_observations(frame, observation)

        # 6. Context-Aware Security Rule Evaluation
        t_rule_start = time.perf_counter()
        alerts = rule_engine.evaluate_frame(frame, observation, tracked_events)
        for alert in alerts:
            self.alert_repo.save_alert(alert)
        t_rule_ms = round((time.perf_counter() - t_rule_start) * 1000, 2)

        total_ms = round((time.perf_counter() - t0) * 1000, 2)

        logger.info(
            f"Frame Processed: {frame.frame_id} @ {frame.telemetry.location_tag} | "
            f"VLM: {t_vlm_ms}ms, Index: {t_idx_ms}ms, Rules: {t_rule_ms}ms, Total: {total_ms}ms | "
            f"Alerts: {len(alerts)}"
        )

        return {
            "status": "success",
            "frame_id": frame.frame_id,
            "location": frame.telemetry.location_tag,
            "timestamp": frame.timestamp.isoformat(),
            "metrics_ms": {
                "vlm": t_vlm_ms,
                "indexing": t_idx_ms,
                "rules": t_rule_ms,
                "total": total_ms
            },
            "observation": observation.model_dump(),
            "alerts_generated": [a.model_dump() for a in alerts]
        }

frame_processor = FrameProcessor()
