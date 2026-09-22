import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.logger import get_logger

logger = get_logger("database_connection")

POSTGRES_USER = os.getenv("POSTGRES_USER", "bis_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "bis_secure_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "bis_regulatory_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 5})
    # Test connection
    with engine.connect() as conn:
        logger.info(f"Connected to PostgreSQL database: {POSTGRES_DB} on {POSTGRES_HOST}")
except Exception as e:
    logger.warning(f"Could not connect to PostgreSQL at {DATABASE_URL}: {e}. Falling back to local SQLite for database operations.")
    DATABASE_URL = "sqlite:///./bis_local_backup.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from .models import Base
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
