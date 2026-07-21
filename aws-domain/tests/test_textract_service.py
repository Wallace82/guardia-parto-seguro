import pytest
from unittest.mock import AsyncMock, patch
from app.services.textract_service import textract_service
from app.schemas.s3 import S3BucketType
from app.core.config import settings
from botocore.exceptions import ClientError

@pytest.mark.asyncio
async def test_textract_mock_mode():
    with patch.object(settings, "MOCK_AWS", True):
        job_id = await textract_service.start_document_analysis(
            file_name="prontuario.pdf",
            bucket_type=S3BucketType.media
        )
        assert job_id == "mock-job-id-textract-12345"

        status, text, blocks = await textract_service.get_analysis_results(job_id)
        assert status == 'SUCCEEDED'
        assert "RELATÓRIO MÉDICO SIMULADO" in text
        assert blocks[0]['block_type'] == 'LINE'

@pytest.mark.asyncio
async def test_textract_start_success(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.start_document_text_detection.return_value = {'JobId': 'textract-job-id-456'}

        job_id = await textract_service.start_document_analysis(
            file_name="prontuario.pdf",
            bucket_type=S3BucketType.media
        )

        assert job_id == "textract-job-id-456"
        mock_aioboto3_session.client.assert_called_once_with('textract', region_name='us-east-1')
        client_mock.start_document_text_detection.assert_called_once_with(
            DocumentLocation={
                'S3Object': {
                    'Bucket': 'guardia-parto-seguro-media-dev-foton',
                    'Name': 'prontuario.pdf'
                }
            }
        )

@pytest.mark.asyncio
async def test_textract_get_in_progress(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.get_document_text_detection.return_value = {'JobStatus': 'IN_PROGRESS'}

        status, text, blocks = await textract_service.get_analysis_results("job-id-inprogress")
        assert status == 'IN_PROGRESS'
        assert text is None
        assert blocks is None

@pytest.mark.asyncio
async def test_textract_get_succeeded_with_pagination(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        
        # Simula resposta em duas páginas
        response_page1 = {
            'JobStatus': 'SUCCEEDED',
            'NextToken': 'page2-token',
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Primeira linha do prontuário', 'Confidence': 98.5}
            ]
        }
        response_page2 = {
            'JobStatus': 'SUCCEEDED',
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Segunda linha do prontuário', 'Confidence': 99.0}
            ]
        }
        client_mock.get_document_text_detection.side_effect = [response_page1, response_page2]

        status, text, blocks = await textract_service.get_analysis_results("job-id-succeeded")
        assert status == 'SUCCEEDED'
        assert text == "Primeira linha do prontuário\nSegunda linha do prontuário"
        assert len(blocks) == 2
        assert blocks[0]['text'] == "Primeira linha do prontuário"
        assert blocks[1]['text'] == "Segunda linha do prontuário"

        # Verifica se get_document_text_detection foi chamado duas vezes com o token correto
        assert client_mock.get_document_text_detection.call_count == 2
        client_mock.get_document_text_detection.assert_any_call(JobId="job-id-succeeded")
        client_mock.get_document_text_detection.assert_any_call(JobId="job-id-succeeded", NextToken="page2-token")
