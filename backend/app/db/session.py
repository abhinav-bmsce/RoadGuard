from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.core.logging import logger

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )
except Exception as e:
    logger.error(f"Failed to connect to primary DATABASE_URL ({settings.DATABASE_URL}): {e}")
    # Fallback to local SQLite if PostgreSQL connection fails
    sqlite_fallback = "sqlite:///./roadguard_fallback.db"
    logger.warning(f"Falling back to local SQLite database: {sqlite_fallback}")
    engine = create_engine(
        sqlite_fallback,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

