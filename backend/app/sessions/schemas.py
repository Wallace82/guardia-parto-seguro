"""
GuardIA — Sessions Schemas (Pydantic v2)
"""
from datetime import datetime

from pydantic import BaseModel, Field


# --------------- Request ---------------

class SessionCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    patient_code: str = Field(
        min_length=3,
        max_length=64,
        description="Código anonimizado do paciente (não usar nome real — LGPD)",
    )
    notes: str | None = Field(default=None, max_length=2000)


class SessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    status: str | None = None


class ChartPoint(BaseModel):
    label: str
    value: int


class DashboardMetricsOut(BaseModel):
    total_sessions: int
    critical_alerts: int
    average_ira: float
    monthly_distribution: list[ChartPoint]


# --------------- Response ---------------

class MediaFileOut(BaseModel):
    id: int
    media_type: str
    filename: str
    blob_url: str | None
    file_size_bytes: int | None
    status: str
    analysis_score: float | None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: int
    title: str
    patient_code: str
    professional_id: int
    status: str
    iga_score: float | None
    iga_level: str | None
    score_video: float | None
    score_audio: float | None
    score_document: float | None
    score_notes: float | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    media_files: list[MediaFileOut] = []

    model_config = {"from_attributes": True}


class SessionListOut(BaseModel):
    total: int
    items: list[SessionOut]


class SessionCreatedResponse(BaseModel):
    session: SessionOut
    message: str = "Sessão criada com sucesso"
