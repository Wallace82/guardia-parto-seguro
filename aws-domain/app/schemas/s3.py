from pydantic import BaseModel, Field
from enum import Enum

class S3BucketType(str, Enum):
    media = "media"
    reports = "reports"

class PresignedUrlRequest(BaseModel):
    file_name: str = Field(..., description="Nome do arquivo ou caminho dentro do bucket (ex: sessao_123/video.mp4)")
    bucket_type: S3BucketType = Field(default=S3BucketType.media, description="Tipo de bucket: media ou reports")
    expiration_seconds: int = Field(default=3600, description="Tempo de expiração da URL em segundos (padrão 1 hora)")

class PresignedUrlResponse(BaseModel):
    url: str
    file_name: str
    expiration_seconds: int
