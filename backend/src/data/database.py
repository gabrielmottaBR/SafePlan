"""
SafePlan Backend - Database Configuration
Configuração de SQLAlchemy com suporte a SQLite (MVP) e PostgreSQL (Produção)
"""

import logging
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.config.settings import get_settings
from backend.src.data.models import Base

logger = logging.getLogger(__name__)

# Global database engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_factory():
    """Get or create session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            class_=Session,
            expire_on_commit=False,
        )
    return _SessionLocal


def create_db_engine():
    """
    Create SQLAlchemy engine based on settings.
    
    Supports both SQLite (MVP) and PostgreSQL (Production).
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    settings = get_settings()
    
    if settings.use_sqlite:
        logger.info(f"📦 Using SQLite database: {settings.sqlite_path}")
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.debug,
        )
    else:
        logger.info(f"🐘 Using PostgreSQL: {settings.database_host}:{settings.database_port}/{settings.database_name}")
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
            echo=settings.debug,
        )
    
    return engine


def init_db():
    """
    Initialize database tables.
    
    Creates all tables defined in Base.metadata.
    Safe to call multiple times - SQLAlchemy will skip existing tables.
    """
    engine = get_engine()
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False


def drop_all_tables():
    """
    Drop all tables (use with caution!).
    
    Only use for development/testing.
    """
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️  All database tables dropped")


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_db():
    """Close database connection."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("🔌 Database connection closed")
