"""
GuardIA — Video Domain — Fixtures de Teste

Configuração compartilhada para os testes do domínio de vídeo.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def async_client():
    """Cliente HTTP assíncrono para testes da API FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
