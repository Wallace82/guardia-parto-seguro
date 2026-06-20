from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GuardIA - Audio Domain"
    SHARED_MEDIA_DIR: str = "/shared_media"
    
    # Azure Configuration
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "brazilsouth"
    AZURE_SPEECH_LANGUAGE: str = "pt-BR"
    
    class Config:
        env_file = ".env"

settings = Settings()
