from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import setup_logging
import structlog

from app.api.s3_router import router as s3_router
from app.api.textract_router import router as textract_router
from app.api.transcribe_router import router as transcribe_router
from app.api.comprehend_router import router as comprehend_router

setup_logging()
logger = structlog.get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Registrando rotas S3, Textract, Transcribe e Comprehend
app.include_router(s3_router, prefix=f"{settings.API_V1_STR}/s3", tags=["s3"])
app.include_router(textract_router, prefix=f"{settings.API_V1_STR}/textract", tags=["textract"])
app.include_router(transcribe_router, prefix=f"{settings.API_V1_STR}/transcribe", tags=["transcribe"])
app.include_router(comprehend_router, prefix=f"{settings.API_V1_STR}/comprehend", tags=["comprehend"])

@app.get("/health")
async def health_check():
    await logger.ainfo("health_check_requested")
    return {"status": "healthy", "service": "aws-domain", "environment": settings.ENVIRONMENT}

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
