import pytest
from unittest.mock import AsyncMock, patch
from app.services.comprehend_service import comprehend_service
from app.core.config import settings
from botocore.exceptions import ClientError

@pytest.mark.asyncio
async def test_comprehend_mock_mode():
    with patch.object(settings, "MOCK_AWS", True):
        sentiment = await comprehend_service.detect_sentiment("Olá, doutor")
        assert sentiment == "NEUTRAL"

        entities = await comprehend_service.detect_medical_entities("Olá, doutor")
        assert len(entities) == 2
        assert entities[0]['Text'] == "Hipertensão"

@pytest.mark.asyncio
async def test_comprehend_sentiment_success(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.detect_sentiment.return_value = {'Sentiment': 'POSITIVE'}

        sentiment = await comprehend_service.detect_sentiment("Ótimo atendimento", language_code="pt")
        assert sentiment == "POSITIVE"
        mock_aioboto3_session.client.assert_called_once_with('comprehend', region_name='us-east-1')
        client_mock.detect_sentiment.assert_called_once_with(Text="Ótimo atendimento", LanguageCode="pt")

@pytest.mark.asyncio
async def test_comprehend_sentiment_error(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.detect_sentiment.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerException', 'Message': 'Error'}},
            'detect_sentiment'
        )

        with pytest.raises(ClientError):
            await comprehend_service.detect_sentiment("Erro")

@pytest.mark.asyncio
async def test_comprehend_medical_entities_success(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.detect_entities_v2.return_value = {
            'Entities': [
                {'Id': 1, 'Text': 'Diabetes', 'Category': 'MEDICAL_CONDITION', 'Type': 'DX_NAME', 'Score': 0.95}
            ]
        }

        entities = await comprehend_service.detect_medical_entities("Diabetes detectada")
        assert len(entities) == 1
        assert entities[0]['Text'] == "Diabetes"
        mock_aioboto3_session.client.assert_called_once_with('comprehendmedical', region_name='us-east-1')
        client_mock.detect_entities_v2.assert_called_once_with(Text="Diabetes detectada")
