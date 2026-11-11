import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "RoadGuard"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Base project directory
    BASE_DIR: Path = BASE_DIR

    # Database: Default to SQLite for zero-friction local run; switchable to PostgreSQL
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/roadguard.db"

    # Deep Learning Model
    MODEL_PATH: str = str(BASE_DIR / "ml/models/best.pt")
    MODEL_DEVICE: str = "cpu"  # 'cpu', 'mps', or 'cuda'
    MODEL_CONFIDENCE_THRESHOLD: float = 0.25
    MODEL_IOU_THRESHOLD: float = 0.45

    # Storage & Upload limits
    UPLOAD_DIR: str = str(BASE_DIR / "backend/uploads")
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]

    # Ultralytics config dir
    YOLO_CONFIG_DIR: str = "/tmp/ultralytics"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

# Ensure required upload directories exist
for sub in ["images", "annotated", "reports"]:
    Path(settings.UPLOAD_DIR, sub).mkdir(parents=True, exist_ok=True)

# Set YOLO config directory in environment
os.environ["YOLO_CONFIG_DIR"] = settings.YOLO_CONFIG_DIR

