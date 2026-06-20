"""
GuardIA — Audio Domain Service
"""
import structlog
from fastapi import FastAPI, status
from app.api.router import router as api_router
from app.core.config import settings

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.include_router(api_router, prefix="/api/v1/audio", tags=["Audio Analysis"])

@app.get("/api/v1/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/audio/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "audio"}
