"""
GuardIA Parto Seguro — Core Platform API
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.alerts.router import router as alerts_router
from app.auth.router import router as auth_router
from app.config import settings
from app.database import create_tables
from app.sessions.router import router as sessions_router

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    log.info("startup", environment=settings.ENVIRONMENT, version="1.0.0")

    # Em dev, cria tabelas automaticamente (em prod usar Alembic)
    if settings.ENVIRONMENT == "development":
        await create_tables()
        log.info("database_tables_created")

    yield

    log.info("shutdown")


app = FastAPI(
    title="GuardIA Parto Seguro — Core API",
    description="""
Plataforma multimodal de IA para vigilância obstétrica e detecção de violência no parto.

## Autenticação
Use `POST /api/v1/auth/login` para obter um Bearer token e inclua-o no header:
`Authorization: Bearer <seu_token>`

## Papéis RBAC
- **admin** — acesso total
- **gestor** — gerencia profissionais, vê todos os alertas
- **profissional** — cria sessões e vê as próprias
- **auditor** — leitura de relatórios
    """,
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
    """Healthcheck endpoint — utilizado pelo Docker e pelo CI."""
    return {
        "status": "healthy",
        "service": "core-platform",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }
