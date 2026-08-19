from app.core.config import settings
from app.ai.base import BaseVLMEngine
from app.ai.mock_vlm import MockVLMEngine
from app.ai.gemini_vlm import GeminiVLMEngine

def get_vlm_engine() -> BaseVLMEngine:
    if settings.VLM_PROVIDER.lower() == "gemini":
        return GeminiVLMEngine()
    return MockVLMEngine()

vlm_engine = get_vlm_engine()
