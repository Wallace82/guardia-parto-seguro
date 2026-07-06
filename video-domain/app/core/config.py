"""
GuardIA Parto Seguro — Video Domain Configuration

Configurações carregadas de variáveis de ambiente (.env)
conforme definido no docker-compose.yml do projeto.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação do Video Domain."""

    # ── Aplicação ──
    PROJECT_NAME: str = "GuardIA - Video Domain"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SERVICE_PORT: int = 8001
    API_V1_PREFIX: str = "/api/v1"

    # ── Banco de Dados ──
    DATABASE_URL: str = "postgresql+asyncpg://guardia:guardia_dev_pass@postgres-domains:5432/video_db"

    # ── Volume compartilhado (mídias de vídeo) ──
    SHARED_MEDIA_DIR: str = "/shared_media"

    # ── Configuração de Análise de Vídeo ──
    VIDEO_FRAME_SAMPLE_RATE: float = 1.0   # Frames por segundo a analisar
    DEEPFACE_BACKEND: str = "retinaface"    # opencv | ssd | dlib | mtcnn | retinaface | mediapipe
    YOLO_CONFIDENCE_THRESHOLD: float = 0.70 # Limiar mínimo de confiança para detecção YOLO
    MAX_FRAMES_PER_ANALYSIS: int = 1800     # Limite de segurança para frames analisados

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
