"""
Tests Configuration and Fixtures
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from datetime import datetime, timezone

from app.main import app
from app.database import get_db

@pytest.fixture
def mock_db_session():
    """Mock da sessão assíncrona do SQLAlchemy."""
    session = AsyncMock()
    return session

@pytest.fixture
def override_get_db(mock_db_session):
    """Substitui a dependência do banco por um mock."""
    async def _override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def async_client(override_get_db):
    """Cliente HTTP assíncrono para testar rotas do FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

@pytest.fixture
def mock_session():
    """Retorna uma sessão mockada."""
    from app.sessions.models import Session, SessionStatus, MediaFile, MediaStatus
    session = Session(
        id=123,
        title="Sessão de Teste",
        patient_code="patient-123",
        professional_id=1,
        status=SessionStatus.pending,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    video = MediaFile(
        id=1,
        session_id=123,
        media_type="video",
        filename="video.mp4",
        blob_url="http://blob/video.mp4",
        status=MediaStatus.uploaded,
        uploaded_at=datetime.now(timezone.utc)
    )
    audio = MediaFile(
        id=2,
        session_id=123,
        media_type="audio",
        filename="audio.wav",
        blob_url="http://blob/audio.wav",
        status=MediaStatus.uploaded,
        uploaded_at=datetime.now(timezone.utc)
    )
    doc = MediaFile(
        id=3,
        session_id=123,
        media_type="document",
        filename="prontuario.pdf",
        blob_url="http://blob/prontuario.pdf",
        status=MediaStatus.uploaded,
        uploaded_at=datetime.now(timezone.utc)
    )
    
    session.media_files = [video, audio, doc]
    return session
