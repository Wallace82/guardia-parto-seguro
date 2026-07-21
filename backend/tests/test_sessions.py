import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_create_session(async_client, mock_session):
    # Mock para by-passar a dependência CurrentUser
    from app.auth.models import User
    fake_user = User(id=1, role="profissional")
    
    with patch("app.sessions.router.SessionService") as mock_service_cls:
         
        mock_instance = mock_service_cls.return_value
        mock_instance.create = AsyncMock(return_value=mock_session)
        
        # Override a dependência de usuário localmente no app
        from app.main import app
        from app.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: fake_user
        
        response = await async_client.post(
            "/api/v1/sessions/",
            json={"patient_code": "PAC-123", "title": "Sessão Teste", "notes": ""},
            headers={"Authorization": "Bearer fake_token"}
        )
        
        # Removemos o override para não afetar outros testes
        app.dependency_overrides.pop(get_current_user, None)
        
        assert response.status_code == 201
        assert response.json()["session"]["id"] == 123
        assert response.json()["session"]["patient_code"] == "patient-123"

@pytest.mark.asyncio
async def test_list_sessions(async_client, mock_session):
    from app.auth.models import User
    fake_user = User(id=1, role="profissional")
    
    with patch("app.sessions.router.SessionService") as mock_service_cls:
        mock_instance = mock_service_cls.return_value
        # list_sessions returns tuple: (total, items)
        mock_instance.list_sessions = AsyncMock(return_value=(1, [mock_session]))
        
        from app.main import app
        from app.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: fake_user
        
        response = await async_client.get(
            "/api/v1/sessions/",
            headers={"Authorization": "Bearer fake_token"}
        )
        
        app.dependency_overrides.pop(get_current_user, None)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == 123


@pytest.mark.asyncio
async def test_get_session_analysis(async_client, mock_session):
    from app.auth.models import User
    fake_user = User(id=1, role="profissional")
    
    mock_session.status = "completed"
    mock_session.score_video = 75.0
    mock_session.score_audio = 60.0
    mock_session.score_document = 80.0
    
    with patch("app.sessions.router.SessionService") as mock_service_cls, \
         patch("app.orchestrator.domain_client.DomainClient") as mock_client_cls:
         
        mock_instance = mock_service_cls.return_value
        mock_instance.get_by_id = AsyncMock(return_value=mock_session)
        
        mock_client_instance = mock_client_cls.return_value
        mock_client_instance.get_audio_results = AsyncMock(return_value={
            "status": "completed",
            "transcription": "Fica calma.",
            "key_findings": [{"type": "verbalization", "description": "Fica calma.", "timestamp_seconds": 1.0, "confidence": 0.9}]
        })
        mock_client_instance.get_video_results = AsyncMock(return_value={
            "status": "completed",
            "key_findings": [{"type": "emotion", "description": "Dor", "timestamp_seconds": 2.0, "confidence": 0.8}]
        })
        mock_client_instance.correlate_risk = AsyncMock(return_value={
            "justifications": {
                "video": {"text": "Video ok", "key_indicators": [], "recommendation": "Rec1"},
                "audio": {"text": "Audio ok", "key_indicators": [], "recommendation": "Rec2"},
                "document": {"text": "Doc ok", "key_indicators": [], "recommendation": "Rec3"}
            }
        })
        
        from app.main import app
        from app.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: fake_user
        
        response = await async_client.get(
            "/api/v1/sessions/123/analysis",
            headers={"Authorization": "Bearer fake_token"}
        )
        
        app.dependency_overrides.pop(get_current_user, None)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == 123
        assert data["status"] == "completed"
        assert data["transcription"]["full_text"] == "Fica calma."
        assert len(data["video_findings"]) == 1
        assert data["risk_details"]["video"]["recommendation"] == "Rec1"

