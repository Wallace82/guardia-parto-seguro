from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.s3 import S3BucketType

class TranscribeRequest(BaseModel):
    file_name: str = Field(..., description="Nome do arquivo de áudio/vídeo dentro do bucket")
    bucket_type: S3BucketType = Field(default=S3BucketType.media, description="Bucket onde o arquivo está salvo")
    language_code: str = Field(default="pt-BR", description="Idioma do áudio")

class TranscribeJobResponse(BaseModel):
    job_name: str = Field(..., description="Nome do Job de transcrição iniciado na AWS")
    status: str = Field(default="IN_PROGRESS", description="Status inicial")

class TranscribeResultResponse(BaseModel):
    job_name: str
    status: str = Field(..., description="IN_PROGRESS, COMPLETED, FAILED")
    transcript_uri: Optional[str] = Field(None, description="URI para o arquivo JSON com o resultado")
