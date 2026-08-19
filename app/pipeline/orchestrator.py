import asyncio
from typing import Optional, Dict, Any
from app.pipeline.simulator import generate_simulated_packets
from app.pipeline.processor import frame_processor
from app.core.config import settings
from app.core.logging import logger

class PipelineManager:
    """
    Manages the lifecycle of asynchronous background video and telemetry processing.
    """
    def __init__(self):
        self._is_running = False
        self._task: Optional[asyncio.Task] = None
        self._processed_count = 0
        self._last_processed_frame: Optional[str] = None

    @property
    def is_running(self) -> bool:
        return self._is_running

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self._is_running,
            "processed_count": self._processed_count,
            "last_processed_frame": self._last_processed_frame,
            "pipeline_interval_seconds": settings.PIPELINE_INTERVAL_SECONDS
        }

    async def start_pipeline(self):
        if self._is_running:
            logger.warning("Pipeline is already active.")
            return

        self._is_running = True
        logger.info("Autonomous Drone Ingestion & Processing Pipeline started.")
        self._task = asyncio.create_task(self._run_loop())

    async def stop_pipeline(self):
        if not self._is_running:
            return

        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Autonomous Drone Ingestion Pipeline stopped.")

    async def _run_loop(self):
        packets = generate_simulated_packets()
        try:
            for packet in packets:
                if not self._is_running:
                    break
                
                result = frame_processor.process_frame(packet)
                if result.get("status") == "success":
                    self._processed_count += 1
                    self._last_processed_frame = packet.frame_id
                
                await asyncio.sleep(settings.PIPELINE_INTERVAL_SECONDS)
                
            logger.info(f"Stream simulation feed completed. Total frames processed in run: {self._processed_count}")
        except asyncio.CancelledError:
            logger.info("Pipeline loop cancelled.")
        except Exception as e:
            logger.error(f"Error in pipeline loop: {e}")
        finally:
            self._is_running = False

pipeline_manager = PipelineManager()
