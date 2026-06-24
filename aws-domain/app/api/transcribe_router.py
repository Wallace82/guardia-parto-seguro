from fastapi import APIRouter, HTTPException, status
from app.schemas.transcribe import TranscribeRequest, TranscribeJobResponse, TranscribeResultResponse
from app.services.transcribe_service import transcribe_service
from botocore.exceptions import ClientError
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/start", response_model=TranscribeJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_transcription(request: TranscribeRequest):
    """
    Inicia o processamento assíncrono de um áudio via Amazon Transcribe.
    """
    try:
        job_name = await transcribe_service.start_transcription(
            file_name=request.file_name,
            bucket_type=request.bucket_type,
            language_code=request.language_code
        )
        return TranscribeJobResponse(job_name=job_name)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await logger.aerror("unhandled_error_transcribe_start", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/result/{job_name}", response_model=TranscribeResultResponse)
async def get_transcription_result(job_name: str):
    """
    Consulta o status e o resultado do Job de transcrição.
    """
    try:
        job_status, transcript_uri = await transcribe_service.get_transcription_results(job_name)
        return TranscribeResultResponse(
            job_name=job_name,
            status=job_status,
            transcript_uri=transcript_uri
        )
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await logger.aerror("unhandled_error_transcribe_result", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
