"""
Tests Configuration and Fixtures
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_session():
    """Retorna uma sessão mockada."""
    from app.sessions.models import Session, SessionStatus, MediaFile, MediaStatus
    session = Session(
        id=123,
        title="Sessão de Teste",
        patient_code="patient-123",
        professional_id=1,
        status=SessionStatus.pending
    )
    
    video = MediaFile(
        id=1,
        session_id=123,
        media_type="video",
        filename="video.mp4",
        blob_url="http://blob/video.mp4",
        status=MediaStatus.uploaded
    )
    audio = MediaFile(
        id=2,
        session_id=123,
        media_type="audio",
        filename="audio.wav",
        blob_url="http://blob/audio.wav",
        status=MediaStatus.uploaded
    )
    doc = MediaFile(
        id=3,
        session_id=123,
        media_type="document",
        filename="prontuario.pdf",
        blob_url="http://blob/prontuario.pdf",
        status=MediaStatus.uploaded
    )
    
    session.media_files = [video, audio, doc]
    return session
