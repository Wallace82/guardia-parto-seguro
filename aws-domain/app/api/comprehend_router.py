from fastapi import APIRouter, HTTPException, status
from app.schemas.comprehend import ComprehendSentimentRequest, ComprehendSentimentResponse, ComprehendMedicalRequest, ComprehendMedicalResponse
from app.services.comprehend_service import comprehend_service
from botocore.exceptions import ClientError
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/sentiment", response_model=ComprehendSentimentResponse)
async def analyze_sentiment(request: ComprehendSentimentRequest):
    """
    Analisa o sentimento de um texto via Amazon Comprehend.
    """
    try:
        sentiment = await comprehend_service.detect_sentiment(
            text=request.text,
            language_code=request.language_code
        )
        return ComprehendSentimentResponse(sentiment=sentiment)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await logger.aerror("unhandled_error_comprehend_sentiment", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/medical", response_model=ComprehendMedicalResponse)
async def analyze_medical_entities(request: ComprehendMedicalRequest):
    """
    Extrai entidades médicas de um texto via Amazon Comprehend Medical.
    """
    try:
        entities = await comprehend_service.detect_medical_entities(text=request.text)
        return ComprehendMedicalResponse(entities=entities)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await logger.aerror("unhandled_error_comprehend_medical", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
