import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://guardia:guardia_dev_pass@postgres-domains:5432/report_db")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8005"))
    AZURE_BLOB_CONNECTION_STRING: str | None = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    AZURE_BLOB_CONTAINER_REPORTS: str = os.getenv("AZURE_BLOB_CONTAINER_REPORTS", "guardia-reports")
    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "./generated_reports")

    class Config:
        env_file = ".env"

settings = Settings()
