"""
GuardIA — Video Domain — API Router

Endpoints REST para análise de vídeo obstétrico.
Porta: 8001 | Prefixo: /api/v1/video
"""
from fastapi import APIRouter, status, BackgroundTasks, HTTPException
import structlog

from app.api.schemas import (
    VideoAnalyzeRequest,
    VideoAnalyzeResponse,
    VideoResultsResponse,
)
from app.services.processor import VideoProcessor

log = structlog.get_logger(__name__)

router = APIRouter()

# Instância singleton do processador de vídeo
_processor = VideoProcessor()


@router.post(
    "/analyze",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=VideoAnalyzeResponse,
    summary="Iniciar análise de vídeo",
    description=(
        "Recebe um arquivo de vídeo (via blob_url) e inicia o processamento "
        "em background utilizando OpenCV, DeepFace, MediaPipe e YOLOv8. "
        "Retorna imediatamente com o ID do job para consulta posterior."
    ),
)
async def analyze(data: VideoAnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Inicia a análise de vídeo em background (RF-007 a RF-014).
    O processamento é assíncrono via BackgroundTasks do FastAPI.
    """
    log.info(
        "video.analyze.requested",
        session_id=data.session_id,
        media_id=data.media_id,
        blob_url=data.blob_url,
    )

    # Enfileira o processamento em background para não travar o core-api
    background_tasks.add_task(_processor.process_video, data.session_id, data.media_id, data.blob_url)

    return VideoAnalyzeResponse(
        job_id=data.media_id,  # Usando media_id como job_id para suportar múltiplos vídeos por sessão
        status="processing",
        message="Processamento de vídeo iniciado em background",
    )


@router.get(
    "/results/{job_id}",
    status_code=status.HTTP_200_OK,
    response_model=VideoResultsResponse,
    summary="Consultar resultado da análise",
    description=(
        "Retorna o resultado completo da análise de vídeo para o identificador informado (media_id ou session_id), "
        "incluindo IGA score, sub-scores por componente e achados relevantes."
    ),
)
async def results(job_id: str):
    """
    Consulta o resultado da análise de vídeo.
    Retorna status 'processing_or_not_found' se o processamento ainda não concluiu.
    """
    result = _processor.get_result(job_id)

    if not result:
        return VideoResultsResponse(
            session_id=job_id,
            status="processing_or_not_found",
        )

    # Garante que o session_id esteja no resultado para validação de schema
    if isinstance(result, dict) and "session_id" not in result:
        result = {**result, "session_id": job_id}

    return result
