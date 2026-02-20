"""
Configuration management for SafePlan application.
Loads and provides access to all application settings from environment variables and config files.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Configurações da aplicação SafePlan"""

    # ==================== PI Server ====================
    PI_SERVER_HOST: str = os.getenv('PI_SERVER_HOST', 'pi-server.petrobras.local')
    PI_SERVER_USERNAME: str = os.getenv('PI_SERVER_USERNAME', '')
    PI_SERVER_PASSWORD: str = os.getenv('PI_SERVER_PASSWORD', '')
    PI_DATA_ARCHIVE: str = os.getenv('PI_DATA_ARCHIVE', 'DEFAULT')
    PI_REQUEST_TIMEOUT: int = int(os.getenv('PI_REQUEST_TIMEOUT', '30'))

    # ==================== Database ====================
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./safeplan.db')
    DATABASE_ECHO_SQL: bool = os.getenv('DATABASE_ECHO_SQL', 'false').lower() == 'true'
    DATABASE_POOL_SIZE: int = int(os.getenv('DATABASE_POOL_SIZE', '20'))

    # ==================== Alerting ====================
    TEAMS_WEBHOOK_URL: str = os.getenv('TEAMS_WEBHOOK_URL', '')
    ALERT_CHECK_INTERVAL_SEC: int = int(os.getenv('ALERT_CHECK_INTERVAL_SEC', '25'))
    ALERT_RETENTION_DAYS: int = int(os.getenv('ALERT_RETENTION_DAYS', '90'))
    ALERT_RETRY_MAX_ATTEMPTS: int = int(os.getenv('ALERT_RETRY_MAX_ATTEMPTS', '3'))
    ALERT_RETRY_BACKOFF_SECONDS: int = int(os.getenv('ALERT_RETRY_BACKOFF_SECONDS', '5'))

    # ==================== ML Models ====================
    ML_MODEL_RETRAINING_DAY: str = os.getenv('ML_MODEL_RETRAINING_DAY', 'Sunday')
    ML_MODEL_RETRAINING_HOUR: str = os.getenv('ML_MODEL_RETRAINING_HOUR', '02:00')
    ANOMALY_THRESHOLD: float = float(os.getenv('ANOMALY_THRESHOLD', '0.7'))
    ML_DATA_WINDOW_DAYS: int = int(os.getenv('ML_DATA_WINDOW_DAYS', '60'))
    FORECAST_HORIZON_HOURS: int = int(os.getenv('FORECAST_HORIZON_HOURS', '24'))

    # ==================== Streaming & UI ====================
    STREAMLIT_SERVER_HEADLESS: bool = os.getenv('STREAMLIT_SERVER_HEADLESS', 'true').lower() == 'true'
    DASHBOARD_REFRESH_INTERVAL_SEC: int = int(os.getenv('DASHBOARD_REFRESH_INTERVAL_SEC', '25'))

    # ==================== Logging & Debug ====================
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/safeplan.log')

    @classmethod
    def validate(cls) -> bool:
        """
        Valida configurações críticas da aplicação.

        Returns:
            True se configurações válidas, False caso contrário
        """
        errors = []

        # Valida PI Server
        if not cls.PI_SERVER_HOST:
            errors.append("PI_SERVER_HOST not configured")
        if not cls.PI_SERVER_USERNAME:
            errors.append("PI_SERVER_USERNAME not configured")
        if not cls.PI_SERVER_PASSWORD:
            errors.append("PI_SERVER_PASSWORD not configured")

        # Valida Database
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL not configured")

        if errors:
            print("[ERROR] Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    @classmethod
    def get_summary(cls) -> dict:
        """Retorna resumo das configurações ativas"""
        return {
            'PI_SERVER': {
                'host': cls.PI_SERVER_HOST,
                'archive': cls.PI_DATA_ARCHIVE,
                'timeout_sec': cls.PI_REQUEST_TIMEOUT
            },
            'DATABASE': {
                'url': cls.DATABASE_URL,
                'pool_size': cls.DATABASE_POOL_SIZE,
                'echo_sql': cls.DATABASE_ECHO_SQL
            },
            'ALERTING': {
                'check_interval_sec': cls.ALERT_CHECK_INTERVAL_SEC,
                'retention_days': cls.ALERT_RETENTION_DAYS,
                'teams_webhook_configured': bool(cls.TEAMS_WEBHOOK_URL)
            },
            'ML': {
                'retraining_day': cls.ML_MODEL_RETRAINING_DAY,
                'retraining_hour': cls.ML_MODEL_RETRAINING_HOUR,
                'anomaly_threshold': cls.ANOMALY_THRESHOLD,
                'data_window_days': cls.ML_DATA_WINDOW_DAYS,
                'forecast_horizon_hours': cls.FORECAST_HORIZON_HOURS
            },
            'UI': {
                'refresh_interval_sec': cls.DASHBOARD_REFRESH_INTERVAL_SEC
            },
            'DEBUG': {
                'debug_mode': cls.DEBUG_MODE,
                'log_level': cls.LOG_LEVEL
            }
        }


def get_config() -> Config:
    """Retorna instância de Config"""
    return Config()


# Alias para conveniência
config = get_config()
