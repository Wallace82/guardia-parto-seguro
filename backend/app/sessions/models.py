"""
GuardIA — Sessions Models (SQLAlchemy)
Session: representa uma consulta/parto sendo monitorado
MediaFile: arquivo de vídeo, áudio ou documento da sessão
"""
import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SessionStatus(str, enum.Enum):
    pending = "pending"         # criada, aguardando mídia
    processing = "processing"   # análise em andamento
    completed = "completed"     # IRA calculado
    error = "error"             # falha no processamento


class MediaType(str, enum.Enum):
    video = "video"
    audio = "audio"
    document = "document"


class MediaStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    analyzed = "analyzed"
    error = "error"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    professional_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        Enum(SessionStatus, name="session_status"),
        default=SessionStatus.pending,
        nullable=False,
    )

    # IRA calculado (preenchido após processamento)
    ira_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ira_level: Mapped[str | None] = mapped_column(String(20), nullable=True)  # baixo/moderado/critico
    score_video: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_audio: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_document: Mapped[float | None] = mapped_column(Float, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    media_files: Mapped[list["MediaFile"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session id={self.id} patient={self.patient_code} status={self.status}>"


class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    media_type: Mapped[str] = mapped_column(
        Enum(MediaType, name="media_type"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    blob_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(MediaStatus, name="media_status"),
        default=MediaStatus.uploaded,
        nullable=False,
    )
    analysis_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["Session"] = relationship(back_populates="media_files")
