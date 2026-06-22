from fastapi import APIRouter, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from app.services.processor import AudioProcessor

router = APIRouter()

class AudioAnalyzeRequest(BaseModel):
    session_id: str
    media_id: str
    blob_url: str
    language: str = "pt-BR"
    options: Optional[dict] = None

class AudioAnalyzeResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED, response_model=AudioAnalyzeResponse)
async def analyze(data: AudioAnalyzeRequest, background_tasks: BackgroundTasks):
    processor = AudioProcessor()
    
    # Processa o áudio em background
    background_tasks.add_task(processor.process_audio, data.session_id, data.blob_url)
    
    return AudioAnalyzeResponse(
        job_id=data.session_id,
        status="processing",
        message="Processamento de áudio com AWS iniciado em background"
    )

@router.get("/results/{session_id}", status_code=status.HTTP_200_OK)
async def results(session_id: str):
    processor = AudioProcessor()
    result = processor.get_result(session_id)
    if not result:
        return {"status": "processing_or_not_found"}
    return result
