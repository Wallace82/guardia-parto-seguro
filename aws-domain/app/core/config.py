from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=(".env", "../.env"),
        extra="ignore"
    )
    
    PROJECT_NAME: str = "GuardIA - AWS Integration Domain"
    API_V1_STR: str = "/api/v1"
    
    AWS_REGION: str = "us-east-1"
    ENVIRONMENT: str = "dev"
    PROJECT_PREFIX: str = "guardia-parto-seguro"
    
    # S3 Buckets
    MEDIA_BUCKET_NAME: str = "guardia-parto-seguro-media-dev-foton"
    REPORTS_BUCKET_NAME: str = "guardia-parto-seguro-reports-dev-foton"

    # Mock AWS for local development
    MOCK_AWS: bool = True

settings = Settings()
