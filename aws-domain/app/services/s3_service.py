import aioboto3
from botocore.exceptions import ClientError
import structlog
from app.core.config import settings
from app.schemas.s3 import S3BucketType

logger = structlog.get_logger()

class S3Service:
    def __init__(self):
        self.session = aioboto3.Session()

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
            async with self.session.client('s3', region_name=settings.AWS_REGION) as s3_client:
                url = await s3_client.generate_presigned_url(
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
