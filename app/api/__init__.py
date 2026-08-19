from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.logs import router as logs_router
from app.api.alerts import router as alerts_router
from app.api.events import router as events_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.summary import router as summary_router
from app.api.pipeline import router as pipeline_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(logs_router)
api_router.include_router(alerts_router)
api_router.include_router(events_router)
api_router.include_router(search_router)
api_router.include_router(chat_router)
api_router.include_router(summary_router)
api_router.include_router(pipeline_router)

__all__ = ["api_router"]
