"""
SafePlan Backend - FastAPI Application Entry Point
Phase 1: MVP Backend (March 2026)

Main application factory and startup configuration.
Includes routes for:
  - Sensor monitoring and management
  - Real-time data collection
  - Anomaly detection and alerting
  - Forecasting and analytics
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.config.settings import get_settings
from backend.src.data.database import init_db, close_db, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events.
    
    Startup: Initialize database, cache, scheduler
    Shutdown: Cleanup resources
    """
    # Startup
    logger.info("🚀 SafePlan Backend starting...")
    logger.info(f"Environment: {get_settings().environment}")
    
    # Initialize database
    if init_db():
        logger.info("✅ Database initialized")
    else:
        logger.error("❌ Failed to initialize database")
    
    yield
    
    # Shutdown
    logger.info("🛑 SafePlan Backend shutting down...")
    close_db()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        lifespan=lifespan,
    )
    
    # CORS Configuration for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for load balancers and monitoring."""
        return {
            "status": "healthy",
            "service": "safeplan-backend",
            "environment": settings.environment,
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """API information endpoint."""
        return {
            "name": settings.api_title,
            "version": settings.api_version,
            "description": settings.api_description,
            "phase": "Phase 1: Backend MVP",
            "database": "SQLite (MVP)" if settings.use_sqlite else "PostgreSQL",
        }
    
    # Metrics endpoint
    @app.get("/stats", tags=["Stats"])
    async def get_stats(db: Session = Depends(get_db)):
        """Get database statistics."""
        from backend.src.data.models import SensorConfig, SensorReading
        
        sensor_count = db.query(SensorConfig).count()
        reading_count = db.query(SensorReading).count()
        
        return {
            "sensors_total": sensor_count,
            "readings_total": reading_count,
            "database": "SQLite (MVP)" if settings.use_sqlite else "PostgreSQL",
        }
    
    # TODO: Import and include routes
    # from backend.src.api.routers import sensors, monitoring, alerts
    # app.include_router(sensors.router)
    # app.include_router(monitoring.router)
    # app.include_router(alerts.router)
    
    # Include sensor routes
    from backend.src.api.sensors import router as sensors_router
    app.include_router(sensors_router)
    
    logger.info("✅ FastAPI application created successfully")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    """Run the application with uvicorn."""
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
