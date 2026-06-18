"""
GuardIA Parto Seguro — Core Platform API
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.sessions.router import router as sessions_router
from app.alerts.router import router as alerts_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # Startup
    print(f"🚀 GuardIA Core Platform starting — Environment: {settings.ENVIRONMENT}")
    yield
    # Shutdown
    print("🛑 GuardIA Core Platform shutting down...")


app = FastAPI(
    title="GuardIA Parto Seguro — Core API",
    description="Plataforma multimodal de IA para vigilância obstétrica",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://frontend:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(sessions_router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["Alerts"])


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Healthcheck endpoint."""
    return {"status": "healthy", "service": "core-platform", "version": "1.0.0"}
