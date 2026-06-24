import boto3
from botocore.exceptions import ClientError
import structlog
from typing import Tuple, List, Optional
from app.core.config import settings
from app.schemas.s3 import S3BucketType

logger = structlog.get_logger()

class TextractService:
    def __init__(self):
        self.textract_client = boto3.client('textract', region_name=settings.AWS_REGION)

    def _get_bucket_name(self, bucket_type: S3BucketType) -> str:
        if bucket_type == S3BucketType.media:
            return settings.MEDIA_BUCKET_NAME
        elif bucket_type == S3BucketType.reports:
            return settings.REPORTS_BUCKET_NAME
        raise ValueError(f"Unknown bucket type: {bucket_type}")

    async def start_document_analysis(self, file_name: str, bucket_type: S3BucketType) -> str:
        """
        Inicia a análise de um documento de forma assíncrona. Retorna o JobId.
        """
        if settings.MOCK_AWS:
            await logger.ainfo("textract_job_started_mock", file=file_name)
            return "mock-job-id-textract-12345"

        bucket_name = self._get_bucket_name(bucket_type)
        try:
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': file_name
                    }
                }
            )
            job_id = response['JobId']
            await logger.ainfo("textract_job_started", job_id=job_id, file=file_name, bucket=bucket_name)
            return job_id
        except ClientError as e:
            await logger.aerror("textract_start_error", error=str(e), file=file_name)
            raise e

    async def get_analysis_results(self, job_id: str) -> Tuple[str, Optional[str], Optional[List[dict]]]:
        """
        Consulta o status do Job. Se estiver concluído, retorna (status, full_text, blocks).
        """
        if settings.MOCK_AWS:
            await logger.ainfo("textract_job_succeeded_mock", job_id=job_id)
            blocks_mock = [{'block_type': 'LINE', 'text': 'RELATÓRIO MÉDICO SIMULADO (MOCK)', 'confidence': 99.9}]
            return 'SUCCEEDED', 'RELATÓRIO MÉDICO SIMULADO (MOCK)', blocks_mock

        try:
            response = self.textract_client.get_document_text_detection(JobId=job_id)
            status = response['JobStatus']

            if status != 'SUCCEEDED':
                return status, None, None

            # Processamento de páginas
            blocks = []
            full_text = ""
            
            # Paginador para documentos muito grandes
            while True:
                for block in response.get('Blocks', []):
                    block_type = block.get('BlockType')
                    text = block.get('Text')
                    if block_type == 'LINE' and text:
                        full_text += text + "\n"
                    blocks.append({
                        'block_type': block_type,
                        'text': text,
                        'confidence': block.get('Confidence')
                    })
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
                response = self.textract_client.get_document_text_detection(JobId=job_id, NextToken=next_token)

            await logger.ainfo("textract_job_succeeded", job_id=job_id, blocks_count=len(blocks))
            return status, full_text.strip(), blocks

        except ClientError as e:
            await logger.aerror("textract_get_error", error=str(e), job_id=job_id)
            raise e

textract_service = TextractService()
