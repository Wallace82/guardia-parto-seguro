from fastapi import APIRouter, HTTPException
from app.schemas.s3 import PresignedUrlRequest, PresignedUrlResponse
from app.services.s3_service import s3_service
from botocore.exceptions import ClientError
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/upload-url", response_model=PresignedUrlResponse)
async def get_presigned_upload_url(request: PresignedUrlRequest):
    """
    Retorna uma URL temporária (Pre-signed URL) para UPLOAD seguro via PUT HTTP.
    """
    try:
        url = await s3_service.generate_presigned_url(
            client_method='put_object',
            file_name=request.file_name,
            bucket_type=request.bucket_type,
            expiration=request.expiration_seconds
        )
        return PresignedUrlResponse(
            url=url,
            file_name=request.file_name,
            expiration_seconds=request.expiration_seconds
        )
    except Exception as e:
        await logger.aerror("upload_url_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Não foi possível gerar a URL de upload")

@router.post("/download-url", response_model=PresignedUrlResponse)
async def get_presigned_download_url(request: PresignedUrlRequest):
    """
    Retorna uma URL temporária (Pre-signed URL) para DOWNLOAD seguro via GET HTTP.
    """
    try:
        url = await s3_service.generate_presigned_url(
            client_method='get_object',
            file_name=request.file_name,
            bucket_type=request.bucket_type,
            expiration=request.expiration_seconds
        )
        return PresignedUrlResponse(
            url=url,
            file_name=request.file_name,
            expiration_seconds=request.expiration_seconds
        )
    except Exception as e:
        await logger.aerror("download_url_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Não foi possível gerar a URL de download")
