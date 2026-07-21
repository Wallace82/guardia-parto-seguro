from fastapi import APIRouter, HTTPException
from app.schemas.textract import TextractAnalyzeRequest, TextractJobResponse, TextractResultResponse
from app.services.textract_service import textract_service
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/analyze", response_model=TextractJobResponse)
async def start_analysis(request: TextractAnalyzeRequest):
    """
    Inicia o processamento OCR assíncrono via Amazon Textract.
    Retorna o job_id para polling.
    """
    try:
        job_id = await textract_service.start_document_analysis(
            file_name=request.file_name,
            bucket_type=request.bucket_type
        )
        return TextractJobResponse(job_id=job_id)
    except Exception as e:
        await logger.aerror("start_analysis_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Erro ao iniciar análise no Textract")

@router.get("/results/{job_id}", response_model=TextractResultResponse)
async def get_results(job_id: str):
    """
    Consulta o status do job de OCR. Se concluído, retorna o texto extraído.
    """
    try:
        status, full_text, blocks = await textract_service.get_analysis_results(job_id)
        return TextractResultResponse(
            job_id=job_id,
            status=status,
            extracted_text=full_text,
            blocks=blocks
        )
    except Exception as e:
        await logger.aerror("get_analysis_results_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Erro ao consultar resultados no Textract")
