import aioboto3
from botocore.exceptions import ClientError
import structlog
from typing import List, Dict
from app.core.config import settings

logger = structlog.get_logger()

class ComprehendService:
    def __init__(self):
        self.session = aioboto3.Session()

    async def detect_sentiment(self, text: str, language_code: str = 'pt') -> str:
        """
        Detecta o sentimento de um texto (e.g. transcrição de áudio).
        """
        if settings.MOCK_AWS:
            await logger.ainfo("comprehend_sentiment_mock", text_length=len(text))
            return "NEUTRAL"
            
        try:
            # Amazon Comprehend suporta 'pt'
            async with self.session.client('comprehend', region_name=settings.AWS_REGION) as comprehend_client:
                response = await comprehend_client.detect_sentiment(
                    Text=text,
                    LanguageCode=language_code
                )
            sentiment = response['Sentiment']
            await logger.ainfo("comprehend_sentiment_success", sentiment=sentiment)
            return sentiment
        except ClientError as e:
            await logger.aerror("comprehend_sentiment_error", error=str(e))
            raise e

    async def detect_medical_entities(self, text: str) -> List[Dict]:
        """
        Detecta entidades médicas usando o Comprehend Medical.
        Nota: Comprehend Medical tem suporte limitado a pt-BR nativamente na API principal,
        mas pode ser mockado para estruturação da aplicação.
        """
        if settings.MOCK_AWS:
            await logger.ainfo("comprehend_medical_mock", text_length=len(text))
            return [
                {"Id": 1, "Text": "Hipertensão", "Category": "MEDICAL_CONDITION", "Type": "DX_NAME", "Score": 0.99},
                {"Id": 2, "Text": "Aspirina", "Category": "MEDICATION", "Type": "BRAND_NAME", "Score": 0.98}
            ]
            
        try:
            async with self.session.client('comprehendmedical', region_name=settings.AWS_REGION) as comprehend_medical:
                response = await comprehend_medical.detect_entities_v2(Text=text)
            entities = response.get('Entities', [])
            await logger.ainfo("comprehend_medical_success", entities_count=len(entities))
            return entities
        except ClientError as e:
            await logger.aerror("comprehend_medical_error", error=str(e))
            raise e

comprehend_service = ComprehendService()
