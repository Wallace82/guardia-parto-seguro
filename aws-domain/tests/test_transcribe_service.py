import pytest
from unittest.mock import AsyncMock, patch
from app.services.transcribe_service import transcribe_service
from app.schemas.s3 import S3BucketType
from app.core.config import settings
from botocore.exceptions import ClientError

@pytest.mark.asyncio
async def test_transcribe_mock_mode():
    with patch.object(settings, "MOCK_AWS", True):
        job_name = await transcribe_service.start_transcription(
            file_name="audio.mp3",
            bucket_type=S3BucketType.media
        )
        assert job_name == "transcribe-audio.mp3"

        status, uri = await transcribe_service.get_transcription_results(job_name)
        assert status == 'COMPLETED'
        assert uri == 'https://mock-s3-url.com/transcript.json'

@pytest.mark.asyncio
async def test_transcribe_start_success(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.start_transcription_job.return_value = {
            'TranscriptionJob': {'TranscriptionJobName': 'transcribe-audio.mp3'}
        }

        job_name = await transcribe_service.start_transcription(
            file_name="audio.mp3",
            bucket_type=S3BucketType.media
        )

        assert job_name == "transcribe-audio.mp3"
        mock_aioboto3_session.client.assert_called_once_with('transcribe', region_name='us-east-1')
        client_mock.start_transcription_job.assert_called_once_with(
            TranscriptionJobName='transcribe-audio.mp3',
            LanguageCode='pt-BR',
            MediaFormat='mp4',
            Media={'MediaFileUri': 's3://guardia-parto-seguro-media-dev-foton/audio.mp3'},
            Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2}
        )

@pytest.mark.asyncio
async def test_transcribe_start_error(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.start_transcription_job.side_effect = ClientError(
            {'Error': {'Code': 'BadRequestException', 'Message': 'Invalid JobName'}},
            'start_transcription_job'
        )

        with pytest.raises(ClientError):
            await transcribe_service.start_transcription(
                file_name="audio.mp3",
                bucket_type=S3BucketType.media
            )

@pytest.mark.asyncio
async def test_transcribe_get_in_progress(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobName': 'transcribe-audio.mp3',
                'TranscriptionJobStatus': 'IN_PROGRESS'
            }
        }

        status, uri = await transcribe_service.get_transcription_results("transcribe-audio.mp3")
        assert status == 'IN_PROGRESS'
        assert uri is None

@pytest.mark.asyncio
async def test_transcribe_get_completed(mock_aioboto3_session):
    with patch.object(settings, "MOCK_AWS", False):
        client_mock = AsyncMock()
        mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
        client_mock.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobName': 'transcribe-audio.mp3',
                'TranscriptionJobStatus': 'COMPLETED',
                'Transcript': {'TranscriptFileUri': 'https://s3.amazonaws.com/results/transcribe-audio.mp3.json'}
            }
        }

        status, uri = await transcribe_service.get_transcription_results("transcribe-audio.mp3")
        assert status == 'COMPLETED'
        assert uri == 'https://s3.amazonaws.com/results/transcribe-audio.mp3.json'
