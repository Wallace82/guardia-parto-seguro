"""
GuardIA — Alerts Schemas (Pydantic v2)
"""
from datetime import datetime

from pydantic import BaseModel, Field


class AlertCreateRequest(BaseModel):
    """Usado internamente pelo motor de risco para criar alertas."""
    session_id: int
    alert_type: str
    severity: str
    title: str = Field(max_length=255)
    description: str
    ira_score: float | None = None


class AlertAcknowledgeRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=1000)


class AlertOut(BaseModel):
    id: int
    session_id: int
    patient_code: str | None = None
    session_title: str | None = None
    alert_type: str
    severity: str
    title: str
    description: str
    ira_score: float | None
    is_acknowledged: bool
    acknowledged_by: int | None
    acknowledged_at: datetime | None
    is_dismissed: bool
    dismissed_by: int | None
    dismissed_at: datetime | None
    email_sent: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertListOut(BaseModel):
    total: int
    items: list[AlertOut]
