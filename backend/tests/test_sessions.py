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
