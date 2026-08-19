from fastapi import APIRouter, HTTPException, Query
from app.storage.repositories import FrameRepository

router = APIRouter(tags=["Logs & Ingested Frames"])
frame_repo = FrameRepository()

@router.get("/logs")
def get_logs(limit: int = Query(default=100, ge=1, le=500)):
    """Fetch all processed structural logs and indexed frames."""
    frames = frame_repo.get_all_frames(limit=limit)
    return {
        "status": "success",
        "total_indexed": len(frames),
        "data": frames
    }

@router.get("/logs/{frame_id}")
def get_frame_by_id(frame_id: str):
    """Fetch a single indexed frame with its detailed telemetry and observation."""
    frame = frame_repo.get_frame(frame_id)
    if not frame:
        raise HTTPException(status_code=404, detail=f"Frame '{frame_id}' not found.")
    return {
        "status": "success",
        "data": frame
    }
