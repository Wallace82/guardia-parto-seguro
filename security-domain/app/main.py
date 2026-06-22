from fastapi import FastAPI
import structlog
from app.services.audit import configure_audit_logging

# Configura logger estruturado (JSON) para envio ao CloudWatch
configure_audit_logging()
logger = structlog.get_logger()

app = FastAPI(
    title="GuardIA - Security & LGPD Domain",
    openapi_url="/api/v1/openapi.json"
)

@app.get("/health")
async def health_check():
    await logger.ainfo("health_check_requested")
    return {"status": "healthy", "service": "security-domain"}

@app.get("/")
async def root():
    return {"message": "Welcome to GuardIA Security Domain"}
