import boto3
from botocore.exceptions import ClientError
import structlog
from app.core.config import settings
from app.schemas.s3 import S3BucketType

logger = structlog.get_logger()

class S3Service:
    def __init__(self):
        # Como o SDK procura por AWS_ACCESS_KEY_ID implicitamente, inicializar o cliente é simples
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)

    def _get_bucket_name(self, bucket_type: S3BucketType) -> str:
        if bucket_type == S3BucketType.media:
            return settings.MEDIA_BUCKET_NAME
        elif bucket_type == S3BucketType.reports:
            return settings.REPORTS_BUCKET_NAME
        raise ValueError(f"Unknown bucket type: {bucket_type}")

    async def generate_presigned_url(self, client_method: str, file_name: str, bucket_type: S3BucketType, expiration: int = 3600, content_type: str = None) -> str:
        """
        Gera uma Pre-signed URL para um objeto no S3.
        :param client_method: 'put_object' (upload) ou 'get_object' (download)
        """
        bucket_name = self._get_bucket_name(bucket_type)
        
        params = {
            'Bucket': bucket_name,
            'Key': file_name
        }
        if content_type and client_method == 'put_object':
            params['ContentType'] = content_type

        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod=client_method,
                Params=params,
                ExpiresIn=expiration
            )
            await logger.ainfo("presigned_url_generated", method=client_method, bucket=bucket_name, file=file_name)
            return url
        except ClientError as e:
            await logger.aerror("error_generating_presigned_url", error=str(e), bucket=bucket_name, file=file_name)
            raise e

s3_service = S3Service()
