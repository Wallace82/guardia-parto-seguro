"""
GuardIA — Video Domain — Schemas Pydantic v2

Schemas de request/response para a API de análise de vídeo,
conforme especificado em API_SPEC.md (Seção 2).
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ── Enums ──

class JobStatus(str, Enum):
    """Status possíveis de um job de análise de vídeo."""
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class FindingType(str, Enum):
    """Tipos de achados na análise de vídeo."""
    emotion = "emotion"
    pose = "pose"
    object = "object"
    bleeding = "bleeding"
    face = "face"


# ── Request Schemas ──

class AnalysisOptions(BaseModel):
    """Opções configuráveis para a análise de vídeo."""
    analyze_emotions: bool = True
    analyze_pose: bool = True
    detect_objects: bool = True
    detect_bleeding: bool = True
    frame_sample_rate: float = Field(default=1.0, ge=0.1, le=30.0, description="Frames por segundo a analisar")


class VideoAnalyzeRequest(BaseModel):
    """Requisição para iniciar análise de vídeo (POST /analyze)."""
    session_id: str = Field(..., description="ID da sessão clínica")
    media_id: str = Field(..., description="ID da mídia no core")
    blob_url: str = Field(..., description="URL/caminho do arquivo de vídeo")
    options: Optional[AnalysisOptions] = None

    model_config = {"json_schema_extra": {
        "example": {
            "session_id": "550e8400-e29b-41d4-a716-446655440002",
            "media_id": "550e8400-e29b-41d4-a716-446655440010",
            "blob_url": "file:///shared_media/video.mp4",
            "options": {
                "analyze_emotions": True,
                "analyze_pose": True,
                "detect_objects": True,
                "detect_bleeding": True,
                "frame_sample_rate": 1.0
            }
        }
    }}


# ── Response Schemas ──

class VideoAnalyzeResponse(BaseModel):
    """Resposta ao iniciar análise de vídeo (202 Accepted)."""
    job_id: str = Field(..., description="ID do job de processamento")
    status: str = Field(default="processing", description="Status inicial do job")
    message: str = Field(default="Processamento de vídeo iniciado em background")


class VideoComponents(BaseModel):
    """Sub-scores individuais da análise de vídeo."""
    emotion_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Score de emoções (DeepFace)")
    pose_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Score de postura (MediaPipe)")
    object_risk_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Score de objetos de risco (YOLOv8)")
    bleeding_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Score de sangramento (OpenCV HSV)")


class KeyFinding(BaseModel):
    """Um achado relevante detectado durante a análise."""
    type: FindingType = Field(..., description="Tipo do achado")
    timestamp_seconds: float = Field(..., ge=0.0, description="Momento no vídeo (segundos)")
    description: str = Field(..., description="Descrição textual do achado")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Nível de confiança da detecção")


class VideoResultsResponse(BaseModel):
    """Resultado completo da análise de vídeo (GET /results/{session_id})."""
    session_id: str
    status: str
    ira_score: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Score de contribuição para o IRA (0-100)")
    components: Optional[VideoComponents] = None
    total_frames: Optional[int] = Field(default=None, ge=0)
    analyzed_frames: Optional[int] = Field(default=None, ge=0)
    key_findings: Optional[List[KeyFinding]] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {
            "session_id": "550e8400-e29b-41d4-a716-446655440002",
            "status": "completed",
            "ira_score": 68.4,
            "components": {
                "emotion_score": 75.2,
                "pose_score": 60.1,
                "object_risk_score": 45.0,
                "bleeding_score": 0.0
            },
            "total_frames": 54000,
            "analyzed_frames": 1800,
            "key_findings": [
                {
                    "type": "emotion",
                    "timestamp_seconds": 135.5,
                    "description": "Expressão de dor detectada com confiança 0.89",
                    "confidence": 0.89
                }
            ],
            "completed_at": "2024-01-15T10:30:00+00:00"
        }
    }}


class HealthResponse(BaseModel):
    """Resposta do healthcheck."""
    status: str = "healthy"
    domain: str = "video"
    version: str = "1.0.0"
    environment: str = "development"
