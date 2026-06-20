import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "domain": "video"}

@pytest.mark.asyncio
async def test_analyze_and_results(async_client: AsyncClient):
    # Envia requisição de análise com blob_url fake
    response = await async_client.post(
        "/api/v1/video/analyze",
        json={
            "session_id": "session-123",
            "media_id": "media-456",
            "blob_url": "file:///shared_media/fake_video.mp4"
        }
    )
    assert response.status_code == 202
    assert response.json()["job_id"] == "session-123"
    assert response.json()["status"] == "processing"
    
    # Busca resultados
    response = await async_client.get("/api/v1/video/results/session-123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert "Arquivo não encontrado" in data["error"]
