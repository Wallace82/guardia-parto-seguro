from fastapi import APIRouter, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from app.services.processor import VideoProcessor

router = APIRouter()

class VideoAnalyzeRequest(BaseModel):
    session_id: str
    media_id: str
    blob_url: str
    options: Optional[dict] = None

class VideoAnalyzeResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED, response_model=VideoAnalyzeResponse)
async def analyze(data: VideoAnalyzeRequest, background_tasks: BackgroundTasks):
    # Opcional: Em um cenário real de longa duração, usaríamos Celery.
    # Para o escopo acadêmico (e simplificação do compose), rodaremos via BackgroundTasks do FastAPI.
    processor = VideoProcessor()
    
    # Enfileira o processamento em background para não travar o core-api
    background_tasks.add_task(processor.process_video, data.session_id, data.blob_url)
    
    return VideoAnalyzeResponse(
        job_id=data.session_id, # Usando session_id como job_id para simplificar
        status="processing",
        message="Processamento de vídeo iniciado em background"
    )

@router.get("/results/{session_id}", status_code=status.HTTP_200_OK)
async def results(session_id: str):
    processor = VideoProcessor()
    result = processor.get_result(session_id)
    if not result:
        return {"status": "processing_or_not_found"}
    return result
