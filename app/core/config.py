from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "Drone Security Analyst Agent"
    LOG_LEVEL: str = "INFO"
    
    # Storage
    DATABASE_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "data" / "drone.db")
    
    # VLM Configuration
    VLM_PROVIDER: str = "mock"  # "mock" or "gemini"
    VLM_MODEL: str = "mock-security-vlm-v1"
    GEMINI_API_KEY: str = ""
    
    # Pipeline Settings
    PIPELINE_INTERVAL_SECONDS: float = 1.0
    PIPELINE_AUTO_START: bool = False
    
    # Detection Thresholds
    LOITERING_MIN_FRAMES: int = 2
    CONFIDENCE_THRESHOLD: float = 0.70

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
