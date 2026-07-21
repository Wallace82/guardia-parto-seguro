from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GuardIA - Audio Domain"
    SHARED_MEDIA_DIR: str = "/shared_media"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    
    class Config:
        env_file = ".env"

settings = Settings()
