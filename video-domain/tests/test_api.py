"""
GuardIA — Video Domain — Testes da API FastAPI

Testes dos endpoints REST do serviço de análise de vídeo.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_generic(async_client: AsyncClient):
    """Testa o endpoint de healthcheck genérico (/api/v1/health)."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["domain"] == "video"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_video(async_client: AsyncClient):
    """Testa o endpoint de healthcheck específico do domínio (/api/v1/video/health)."""
    response = await async_client.get("/api/v1/video/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["domain"] == "video"


@pytest.mark.asyncio
async def test_analyze_returns_202(async_client: AsyncClient):
    """Testa que POST /analyze retorna 202 Accepted com job_id."""
    response = await async_client.post(
        "/api/v1/video/analyze",
        json={
            "session_id": "session-test-001",
            "media_id": "media-test-001",
            "blob_url": "file:///shared_media/fake_video.mp4",
        },
    )
    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] == "media-test-001"
    assert data["status"] == "processing"
    assert "message" in data


@pytest.mark.asyncio
async def test_analyze_with_options(async_client: AsyncClient):
    """Testa que POST /analyze aceita opções de análise."""
    response = await async_client.post(
        "/api/v1/video/analyze",
        json={
            "session_id": "session-test-002",
            "media_id": "media-test-002",
            "blob_url": "file:///shared_media/video.mp4",
            "options": {
                "analyze_emotions": True,
                "analyze_pose": False,
                "detect_objects": True,
                "detect_bleeding": True,
                "frame_sample_rate": 2.0,
            },
        },
    )
    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] == "media-test-002"


@pytest.mark.asyncio
async def test_analyze_validation_error(async_client: AsyncClient):
    """Testa que POST /analyze retorna 422 para payload inválido."""
    response = await async_client.post(
        "/api/v1/video/analyze",
        json={"session_id": "test"},  # Faltam campos obrigatórios
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_results_not_found(async_client: AsyncClient):
    """Testa que GET /results retorna status processing_or_not_found para sessão inexistente."""
    response = await async_client.get("/api/v1/video/results/nonexistent-session")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing_or_not_found"


@pytest.mark.asyncio
async def test_analyze_and_get_results_flow(async_client: AsyncClient):
    """Testa o fluxo completo: envia análise e consulta resultados (arquivo não existe)."""
    # 1. Envia requisição de análise com arquivo inexistente
    response = await async_client.post(
        "/api/v1/video/analyze",
        json={
            "session_id": "session-flow-test",
            "media_id": "media-flow-test",
            "blob_url": "file:///shared_media/non_existent.mp4",
        },
    )
    assert response.status_code == 202

    # 2. Aguarda brevemente para o background task executar
    import asyncio
    await asyncio.sleep(0.5)

    # 3. Consulta resultados — deve falhar porque o arquivo não existe
    response = await async_client.get("/api/v1/video/results/session-flow-test")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert "error" in data


@pytest.mark.asyncio
async def test_openapi_docs_available(async_client: AsyncClient):
    """Testa que a documentação Swagger UI está acessível."""
    response = await async_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json_available(async_client: AsyncClient):
    """Testa que o schema OpenAPI JSON está acessível."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "GuardIA - Video Domain"
    assert data["info"]["version"] == "1.0.0"
