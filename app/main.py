import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nicegui import ui

from app.core.config import settings
from app.core.logging import logger
from app.api import api_router
from app.storage.database import db
from app.pipeline.orchestrator import pipeline_manager
from app.storage.repositories import FrameRepository
from app.gui import init_gui

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Drone Security Analyst Agent Services...")
    db.init_db()
    
    frame_repo = FrameRepository()
    if frame_repo.get_frame_count() == 0 or settings.PIPELINE_AUTO_START:
        logger.info("Fresh database detected. Triggering initial ingestion stream...")
        asyncio.create_task(pipeline_manager.start_pipeline())
        
    yield
    
    logger.info("Shutting down Drone Security Analyst Agent Services...")
    await pipeline_manager.stop_pipeline()

app = FastAPI(
    title="Drone Security Analyst Agent API",
    description=(
        "Production-grade Multimodal Drone Security Analyst Agent. "
        "Processes real-time telemetry and video frames, produces structured VLM observations, "
        "indexes frame-by-frame data in SQLite FTS5, detects contextual security anomalies, "
        "and exposes a tool-using Conversational Security Analyst."
    ),
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Mount NiceGUI interactive operations dashboard
init_gui()
ui.run_with(
    app,
    title="Drone Security Analyst SOC",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)