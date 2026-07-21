import pytest
from unittest.mock import AsyncMock, patch

from app.auth.schemas import TokenResponse, UserOut

@pytest.mark.asyncio
async def test_login_success(async_client):
    mock_token = TokenResponse(
        access_token="fake_access_token",
        refresh_token="fake_refresh_token",
        token_type="bearer",
        expires_in=3600
    )
    
    with patch("app.auth.router.AuthService") as mock_service_cls:
        mock_instance = mock_service_cls.return_value
        mock_instance.login = AsyncMock(return_value=mock_token)
        
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "admin@guardia.com", "password": "password123"}
        )
        
        assert response.status_code == 200
        assert response.json()["access_token"] == "fake_access_token"
        mock_instance.login.assert_called_once()

@pytest.mark.asyncio
async def test_refresh_token(async_client):
    mock_token = TokenResponse(
        access_token="new_access_token",
        refresh_token="new_refresh_token",
        token_type="bearer",
        expires_in=3600
    )
    
    with patch("app.auth.router.AuthService") as mock_service_cls:
        mock_instance = mock_service_cls.return_value
        mock_instance.refresh = AsyncMock(return_value=mock_token)
        
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "old_fake_refresh_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["access_token"] == "new_access_token"
        mock_instance.refresh.assert_called_once()
