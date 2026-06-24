from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "GuardIA - AWS Integration Domain"
    API_V1_STR: str = "/api/v1"
    
    AWS_REGION: str = "us-east-1"
    ENVIRONMENT: str = "dev"
    PROJECT_PREFIX: str = "guardia-parto-seguro"
    
    # S3 Buckets
    MEDIA_BUCKET_NAME: str = f"{PROJECT_PREFIX}-media-{ENVIRONMENT}"
    REPORTS_BUCKET_NAME: str = f"{PROJECT_PREFIX}-reports-{ENVIRONMENT}"

    # Mock AWS for local development
    MOCK_AWS: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
