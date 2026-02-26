"""
SafePlan Backend - Settings and Configuration Management
Uses pydantic-settings for environment variable loading
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Can be overridden with a .env file in the project root.
    """
    
    # FastAPI Configuration
    environment: str = "development"
    debug: bool = True
    api_title: str = "SafePlan Backend API"
    api_version: str = "2.0.0"
    api_description: str = "Monitoramento Inteligente de Sensores com IA"
    
    # Database Configuration
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "safeplan_db"
    database_user: str = "safeplan"
    database_password: str = "password"
    
    # Use SQLite for MVP (easier development), migrate to PostgreSQL in Phase 2
    use_sqlite: bool = True
    sqlite_path: str = "safeplan.db"
    
    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy database URL."""
        if self.use_sqlite:
            # SQLite for MVP development - use absolute path to backend/safeplan.db
            import os
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(backend_dir, self.sqlite_path)
            # Return with absolute path
            return f"sqlite:///{db_path.replace(chr(92), '/')}"
        else:
            # PostgreSQL for production
            return (
                f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
                f"@{self.database_host}:{self.database_port}/{self.database_name}"
            )
    
    # Legacy SQLite (for migration reference)
    legacy_sqlite_path: str = "../safeplan.db"
    
    # Security Configuration
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # PI Server Integration
    pi_server_url: Optional[str] = None
    pi_username: Optional[str] = None
    pi_password: Optional[str] = None
    use_pi_server: bool = False
    
    # Monitoring & Alerts
    teams_webhook_url: Optional[str] = None
    alert_check_interval_seconds: int = 60
    max_concurrent_sensors: int = 15000
    
    # Redis Cache
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/safeplan.log"
    
    # ML Models
    ml_model_path: str = "./models/"
    anomaly_threshold: float = 0.85
    forecast_window_days: int = 7
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore unknown fields from .env (for legacy compatibility)


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses LRU cache to avoid reloading environment variables on every call.
    
    Returns:
        Settings: Cached application settings
    """
    return Settings()
