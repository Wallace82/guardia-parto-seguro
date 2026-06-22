from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.s3 import S3BucketType

class TextractAnalyzeRequest(BaseModel):
    file_name: str = Field(..., description="Nome do arquivo dentro do bucket")
    bucket_type: S3BucketType = Field(default=S3BucketType.media, description="Bucket onde o arquivo está salvo")

class TextractJobResponse(BaseModel):
    job_id: str = Field(..., description="ID do Job assíncrono iniciado na AWS")
    status: str = Field(default="IN_PROGRESS", description="Status inicial")

class TextBlock(BaseModel):
    block_type: str
    text: Optional[str] = None
    confidence: Optional[float] = None

class TextractResultResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="IN_PROGRESS, SUCCEEDED, FAILED, PARTIAL_SUCCESS")
    extracted_text: Optional[str] = Field(None, description="Todo o texto extraído unificado")
    blocks: Optional[List[TextBlock]] = Field(None, description="Blocos brutos estruturados (linhas/palavras)")
