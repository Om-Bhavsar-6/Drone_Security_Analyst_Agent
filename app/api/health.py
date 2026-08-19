from fastapi import APIRouter
from app.core.config import settings
from app.storage.repositories import FrameRepository, AlertRepository
from app.pipeline.orchestrator import pipeline_manager

router = APIRouter(tags=["Health & Status"])

frame_repo = FrameRepository()
alert_repo = AlertRepository()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "vlm_provider": settings.VLM_PROVIDER,
        "total_frames_indexed": frame_repo.get_frame_count(),
        "total_alerts": alert_repo.get_alert_count(),
        "pipeline_status": pipeline_manager.get_status()
    }
