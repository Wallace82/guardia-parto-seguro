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
from app.sessions.router import router as sessions_router
from app.sessions.analysis_router import router as analysis_router
from app.middleware.logging import StructlogMiddleware

# Configura o structlog para gerar JSON
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    log.info("startup", environment=settings.ENVIRONMENT, version="1.0.0")

    # Tabelas do banco de dados agora são criadas e controladas via migrações do Alembic.
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
    allow_origins=[
        "http://localhost:4200",   # Angular dev server
        "http://localhost:4300",   # Angular alternativo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observabilidade e Logs
app.add_middleware(StructlogMiddleware)

# Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(sessions_router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(analysis_router)
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
