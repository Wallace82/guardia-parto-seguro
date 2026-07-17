from datetime import datetime
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VideoAnalysis(Base):
    __tablename__ = "video_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    arquivo_video: Mapped[str] = mapped_column(String(512), nullable=False)
    duracao: Mapped[int | None] = mapped_column(Integer, nullable=True) # seconds
    modelo_utilizado: Mapped[str | None] = mapped_column(String(128), nullable=True)
    
    # Scores
    emotion_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    body_language_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    interaction_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    violence_indicator_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    eventos_detectados: Mapped[dict | None] = mapped_column(JSONB, nullable=True) # List of strings stored as JSON
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    resultado_final: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["Session"] = relationship("Session", back_populates="video_analyses")


class AudioAnalysis(Base):
    __tablename__ = "audio_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    arquivo_audio: Mapped[str] = mapped_column(String(512), nullable=False)
    transcricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Scores
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    anxiety_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    communication_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    trauma_indicator_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    analise_comprehend: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    eventos: Mapped[dict | None] = mapped_column(JSONB, nullable=True) # List of strings
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["Session"] = relationship("Session", back_populates="audio_analyses")


class DocumentAnalysis(Base):
    __tablename__ = "document_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    arquivo_documento: Mapped[str] = mapped_column(String(512), nullable=False)
    tipo_documento: Mapped[str | None] = mapped_column(String(128), nullable=True)
    texto_extraido: Mapped[str | None] = mapped_column(Text, nullable=True)
    entidades_detectadas: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Scores
    clinical_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    psychological_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    pregnancy_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    fatores_identificados: Mapped[dict | None] = mapped_column(JSONB, nullable=True) # List of strings
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["Session"] = relationship("Session", back_populates="document_analyses")


class RiskHistory(Base):
    __tablename__ = "risk_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    nivel: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    session: Mapped["Session"] = relationship("Session")


class VideoParticipant(Base):
    __tablename__ = "video_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("video_analysis.id", ondelete="CASCADE"), nullable=False, index=True
    )
    participant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    face_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    speaker_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    role: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    first_frame: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_frame: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    video_analysis: Mapped["VideoAnalysis"] = relationship("VideoAnalysis")


class ParticipantEvent(Base):
    __tablename__ = "participant_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    participant_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    emotion: Mapped[str | None] = mapped_column(String(64), nullable=True)
    body_language: Mapped[str | None] = mapped_column(String(128), nullable=True)
    speech: Mapped[Text | None] = mapped_column(Text, nullable=True)
    alert_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ParticipantObject(Base):
    __tablename__ = "participant_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("video_analysis.id", ondelete="CASCADE"), nullable=False, index=True
    )
    participant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    face_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    object_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    interaction_type: Mapped[str | None] = mapped_column(String(64), nullable=True) # e.g. "manipulando", "proximo"
    timestamp: Mapped[str | None] = mapped_column(String(64), nullable=True)
    frame: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    video_analysis: Mapped["VideoAnalysis"] = relationship("VideoAnalysis")
