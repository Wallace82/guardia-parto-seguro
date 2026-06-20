from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GuardIA - Video Domain"
    SHARED_MEDIA_DIR: str = "/shared_media"
    VIDEO_FRAME_SAMPLE_RATE: float = 1.0  # 1 frame por segundo
    
    class Config:
        env_file = ".env"

settings = Settings()
