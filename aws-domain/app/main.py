from fastapi import FastAPI
from app.core.config import settings
import structlog

from app.api.s3_router import router as s3_router
from app.api.textract_router import router as textract_router

logger = structlog.get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Registrando rotas S3 e Textract
app.include_router(s3_router, prefix=f"{settings.API_V1_STR}/s3", tags=["s3"])
app.include_router(textract_router, prefix=f"{settings.API_V1_STR}/textract", tags=["textract"])

@app.get("/health")
async def health_check():
    await logger.ainfo("health_check_requested")
    return {"status": "healthy", "service": "aws-domain", "environment": settings.ENVIRONMENT}

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
