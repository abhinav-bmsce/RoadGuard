import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.services.inference_engine import inference_engine

# Routers
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.detection import router as detection_router
from backend.app.api.v1.history import router as history_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if not existing
    logger.info("Initializing RoadGuard Database tables...")
    Base.metadata.create_all(bind=engine)

    # Initialize / verify deep learning model
    logger.info("Checking Deep Learning Inference Engine...")
    _ = inference_engine.is_loaded

    yield

    # Shutdown
    logger.info("RoadGuard application shutting down...")


app = FastAPI(
    title="RoadGuard API",
    description="Deep Learning-Based Road Damage Detection and Severity Assessment Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Setup - Allow all local dev hosts, IPs, and ports seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads directory for images, annotated visuals, and reports
uploads_path = Path(settings.UPLOAD_DIR)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Include Routers
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(health_router, tags=["Root Health"])  # Also exposed at /health
app.include_router(detection_router, prefix=settings.API_V1_STR, tags=["Detection"])
app.include_router(history_router, prefix=settings.API_V1_STR, tags=["History"])
app.include_router(analytics_router, prefix=settings.API_V1_STR, tags=["Analytics"])
app.include_router(reports_router, prefix=settings.API_V1_STR, tags=["Reports"])


@app.get("/")
def root():
    return {
        "app": "RoadGuard",
        "description": "Deep Learning-Based Road Damage Detection and Severity Assessment Platform",
        "status": "online",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

