import boto3
from botocore.exceptions import ClientError
import structlog
from typing import Tuple, Optional
from app.core.config import settings
from app.schemas.s3 import S3BucketType

logger = structlog.get_logger()

class TranscribeService:
    def __init__(self):
        self.transcribe_client = boto3.client('transcribe', region_name=settings.AWS_REGION)

    def _get_bucket_name(self, bucket_type: S3BucketType) -> str:
        if bucket_type == S3BucketType.media:
            return settings.MEDIA_BUCKET_NAME
        elif bucket_type == S3BucketType.reports:
            return settings.REPORTS_BUCKET_NAME
        raise ValueError(f"Unknown bucket type: {bucket_type}")

    async def start_transcription(self, file_name: str, bucket_type: S3BucketType, language_code: str = 'pt-BR') -> str:
        """
        Inicia o job de transcrição no Amazon Transcribe.
        """
        job_name = f"transcribe-{file_name.replace('/', '-')}"
        
        if settings.MOCK_AWS:
            await logger.ainfo("transcribe_job_started_mock", file=file_name, job_name=job_name)
            return job_name

        bucket_name = self._get_bucket_name(bucket_type)
        media_uri = f"s3://{bucket_name}/{file_name}"
        
        try:
            response = self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                LanguageCode=language_code,
                MediaFormat='mp4', # Assumindo mp4/mp3
                Media={
                    'MediaFileUri': media_uri
                },
                Settings={
                    'ShowSpeakerLabels': True,
                    'MaxSpeakerLabels': 2
                }
            )
            started_job_name = response['TranscriptionJob']['TranscriptionJobName']
            await logger.ainfo("transcribe_job_started", job_name=started_job_name, file=file_name)
            return started_job_name
        except ClientError as e:
            await logger.aerror("transcribe_start_error", error=str(e), file=file_name)
            raise e

    async def get_transcription_results(self, job_name: str) -> Tuple[str, Optional[str]]:
        """
        Consulta o status da transcrição. Retorna (status, transcript_uri).
        """
        if settings.MOCK_AWS:
            await logger.ainfo("transcribe_job_succeeded_mock", job_name=job_name)
            return 'COMPLETED', 'https://mock-s3-url.com/transcript.json'

        try:
            response = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            
            if status != 'COMPLETED':
                return status, None
                
            transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
            await logger.ainfo("transcribe_job_succeeded", job_name=job_name)
            return status, transcript_uri
            
        except ClientError as e:
            await logger.aerror("transcribe_get_error", error=str(e), job_name=job_name)
            raise e

transcribe_service = TranscribeService()
