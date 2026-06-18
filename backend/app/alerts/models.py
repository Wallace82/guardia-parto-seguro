"""
GuardIA — Alerts Models (SQLAlchemy)
Alert: alerta gerado automaticamente pelo motor de risco
"""
import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AlertSeverity(str, enum.Enum):
    moderate = "moderate"   # IRA 40-69
    critical = "critical"   # IRA >= 70


class AlertType(str, enum.Enum):
    ira_threshold = "ira_threshold"         # IRA ultrapassou limiar
    video_anomaly = "video_anomaly"         # anomalia detectada no vídeo
    audio_keyword = "audio_keyword"         # keyword de risco detectada
    document_inconsistency = "document_inconsistency"  # inconsistência documental
    missing_consent = "missing_consent"     # consentimento ausente


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_type: Mapped[str] = mapped_column(
        Enum(AlertType, name="alert_type"), nullable=False
    )
    severity: Mapped[str] = mapped_column(
        Enum(AlertSeverity, name="alert_severity"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ira_score: Mapped[float | None] = mapped_column(nullable=True)

    # Controle de reconhecimento
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    acknowledged_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Controle de notificação por e-mail
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<Alert id={self.id} type={self.alert_type} severity={self.severity}>"
