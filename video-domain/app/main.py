"""
GuardIA Parto Seguro — Video Domain Service

Microsserviço FastAPI para análise de vídeo obstétrico utilizando
visão computacional local (OpenCV, DeepFace, MediaPipe, YOLOv8).

Porta: 8001
Healthcheck: GET /api/v1/video/health
Swagger UI:  GET /docs
"""
import time
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import setup_logging
from app.api.router import router as video_router
from app.api.schemas import HealthResponse

# ── Logging ──
setup_logging()
log = structlog.get_logger(__name__)


# ── Lifespan (startup/shutdown) ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    log.info(
        "video_service.starting",
        service=settings.PROJECT_NAME,
        port=settings.SERVICE_PORT,
        environment=settings.ENVIRONMENT,
        frame_sample_rate=settings.VIDEO_FRAME_SAMPLE_RATE,
        deepface_backend=settings.DEEPFACE_BACKEND,
        yolo_threshold=settings.YOLO_CONFIDENCE_THRESHOLD,
    )
    yield
    log.info("video_service.shutdown")


# ── FastAPI App ──
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Microsserviço de análise de vídeo obstétrico do GuardIA Parto Seguro. "
        "Processa vídeos clínicos utilizando OpenCV, DeepFace, MediaPipe e YOLOv8 "
        "para detectar indicadores de risco assistencial: expressões de sofrimento, "
        "postura corporal, objetos de risco e sangramento."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "GuardIA Parto Seguro",
        "url": "https://github.com/Wallace82/guardia-parto-seguro",
    },
    license_info={
        "name": "MIT",
    },
)


# ── Middleware: CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Middleware: Logging de Requisições ──
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Registra cada requisição HTTP com tempo de resposta (RNF-012)."""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    log.info(
        "http.request",
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


# ── Rotas ──
app.include_router(
    video_router,
    prefix="/api/v1/video",
    tags=["Video Analysis"],
)


# ── Healthcheck ──
@app.get(
    "/api/v1/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
    tags=["Health"],
    summary="Healthcheck geral do serviço",
)
@app.get(
    "/api/v1/video/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
    tags=["Health"],
    summary="Healthcheck do domínio de vídeo",
)
async def health():
    """
    Endpoint de verificação de saúde (RNF-013).
    Utilizado pelo Docker healthcheck e pelo orquestrador.
    """
    return HealthResponse(
        status="healthy",
        domain="video",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
    )


# ── Handler de Exceções Não Tratadas ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura exceções não tratadas e retorna erro 500 formatado."""
    log.exception(
        "unhandled_exception",
        path=str(request.url.path),
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno no serviço de vídeo",
            "error_type": type(exc).__name__,
        },
    )
