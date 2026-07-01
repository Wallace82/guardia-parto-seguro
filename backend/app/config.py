"""
GuardIA Parto Seguro — Core Platform Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Domain Service URLs
    VIDEO_SERVICE_URL: str = "http://video-service:8001"
    AUDIO_SERVICE_URL: str = "http://audio-service:8002"
    DOCUMENT_SERVICE_URL: str = "http://document-service:8003"
    RISK_SERVICE_URL: str = "http://risk-service:8004"
    REPORT_SERVICE_URL: str = "http://report-service:8005"
    VIDEO_FRAME_SAMPLE_RATE: float = 1.0

    # AWS S3
    AWS_REGION: str = "us-east-1"
    MEDIA_BUCKET_NAME: str = "guardia-media"

    # Notifications
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAIL_GESTOR: str = ""

    # IRA Thresholds
    IRA_THRESHOLD_MODERATE: float = 40.0
    IRA_THRESHOLD_CRITICAL: float = 70.0

    # Upload limits
    MAX_VIDEO_SIZE_MB: int = 2000
    MAX_AUDIO_SIZE_MB: int = 500
    MAX_DOCUMENT_SIZE_MB: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
