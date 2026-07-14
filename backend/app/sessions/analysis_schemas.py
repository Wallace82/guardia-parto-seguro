from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class VideoAnalysisCreate(BaseModel):
    arquivo_video: str
    duracao: Optional[int] = None
    modelo_utilizado: Optional[str] = None
    emotion_score: Optional[float] = None
    body_language_score: Optional[float] = None
    interaction_score: Optional[float] = None
    violence_indicator_score: Optional[float] = None
    eventos_detectados: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    resultado_final: Optional[str] = None

class VideoAnalysisOut(VideoAnalysisCreate):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AudioAnalysisCreate(BaseModel):
    arquivo_audio: str
    transcricao: Optional[str] = None
    sentiment_score: Optional[float] = None
    anxiety_score: Optional[float] = None
    communication_score: Optional[float] = None
    trauma_indicator_score: Optional[float] = None
    analise_comprehend: Optional[Dict[str, Any]] = None
    eventos: Optional[List[str]] = None
    confidence_score: Optional[float] = None

class AudioAnalysisOut(AudioAnalysisCreate):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentAnalysisCreate(BaseModel):
    arquivo_documento: str
    tipo_documento: Optional[str] = None
    texto_extraido: Optional[str] = None
    entidades_detectadas: Optional[Dict[str, Any]] = None
    clinical_risk_score: Optional[float] = None
    psychological_risk_score: Optional[float] = None
    pregnancy_risk_score: Optional[float] = None
    fatores_identificados: Optional[List[str]] = None
    confidence_score: Optional[float] = None

class DocumentAnalysisOut(DocumentAnalysisCreate):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RiskSourcesOut(BaseModel):
    video: Optional[float] = None
    audio: Optional[float] = None
    document: Optional[float] = None

class SessionRiskSummaryOut(BaseModel):
    sessionId: int
    globalScore: float
    riskLevel: str
    sources: RiskSourcesOut
