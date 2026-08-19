from fastapi import APIRouter
from app.pipeline.orchestrator import pipeline_manager

router = APIRouter(tags=["Pipeline Controls"])

@router.post("/pipeline/start")
async def start_pipeline():
    """Start autonomous background processing of simulated drone feeds."""
    await pipeline_manager.start_pipeline()
    return {"status": "success", "message": "Pipeline started", "pipeline": pipeline_manager.get_status()}

@router.post("/pipeline/stop")
async def stop_pipeline():
    """Stop autonomous background processing."""
    await pipeline_manager.stop_pipeline()
    return {"status": "success", "message": "Pipeline stopped", "pipeline": pipeline_manager.get_status()}

@router.get("/pipeline/status")
def get_pipeline_status():
    """Get the current operational status of the processing pipeline."""
    return {"status": "success", "pipeline": pipeline_manager.get_status()}
