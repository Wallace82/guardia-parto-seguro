"""
Tests — Multimodal Orchestrator
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.sessions.models import SessionStatus, MediaStatus
from app.orchestrator.orchestrator import orchestrate_session_analysis

@pytest.mark.asyncio
@patch("app.orchestrator.orchestrator.AsyncSessionLocal")
@patch("app.orchestrator.orchestrator.DomainClient")
@patch("app.orchestrator.orchestrator.AlertService")
async def test_orchestrate_session_analysis_success(
    mock_alert_service_class,
    mock_domain_client_class,
    mock_session_local,
    mock_session
):
    """Testa a orquestração completa com sucesso quando todas as análises concluem."""
    # 1. Configurar Mocks de Banco
    db_mock = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = db_mock
    
    # Mock do retorno do fetch da sessão
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = mock_session
    db_mock.execute.return_value = execute_result
    
    # 2. Configurar Mocks dos Clientes de Domínio
    client_mock = AsyncMock()
    mock_domain_client_class.return_value = client_mock
    
    # Mock das chamadas HTTP
    client_mock.analyze_video.return_value = {"job_id": "video-job", "status": "queued"}
    client_mock.get_video_results.return_value = {"status": "completed", "iga_score": 80.0}
    
    client_mock.analyze_audio.return_value = {"job_id": "audio-job", "status": "queued"}
    client_mock.get_audio_results.return_value = {"status": "completed", "iga_score": 60.0}
    
    client_mock.analyze_document.return_value = {"iga_score": 40.0}
    
    client_mock.correlate_risk.return_value = {
        "iga_score": 63.0,
        "risk_level": "moderado",
        "justifications": {
            "video": {"text": "Indicador de dor"},
            "audio": {"text": "Sinal de estresse"}
        }
    }
    
    # Mock do AlertService
    alert_service_mock = AsyncMock()
    mock_alert_service_class.return_value = alert_service_mock

    # 3. Executar o Orquestrador
    await orchestrate_session_analysis(mock_session.id)

    # 4. Asserts
    # Verificação de status e scores atualizados na Sessão
    assert mock_session.status == SessionStatus.completed
    assert mock_session.iga_score == 63.0
    assert mock_session.iga_level == "moderado"
    assert mock_session.score_video == 80.0
    assert mock_session.score_audio == 60.0
    assert mock_session.score_document == 40.0
    
    # Verificação de chamadas de análise
    client_mock.analyze_video.assert_called_once_with(mock_session.id, 1, "http://blob/video.mp4")
    client_mock.analyze_audio.assert_called_once_with(mock_session.id, 2, "http://blob/audio.wav")
    client_mock.analyze_document.assert_called_once_with(mock_session.id, 3, "http://blob/prontuario.pdf")
    
    # Verificação do calculador de risco e geração de alerta
    client_mock.correlate_risk.assert_called_once_with(
        session_id=mock_session.id,
        patient_code="patient-123",
        video_score=80.0,
        audio_score=60.0,
        document_score=40.0
    )
    alert_service_mock.create_alert.assert_called_once()
    client_mock.generate_report.assert_called_once_with(mock_session.id)

@pytest.mark.asyncio
@patch("app.orchestrator.orchestrator.AsyncSessionLocal")
@patch("app.orchestrator.orchestrator.DomainClient")
async def test_orchestrate_session_analysis_no_media(
    mock_domain_client_class,
    mock_session_local,
    mock_session
):
    """Testa que se a sessão não tiver mídias, ela conclui imediatamente."""
    db_mock = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = db_mock
    
    # Esvazia mídias
    mock_session.media_files = []
    
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = mock_session
    db_mock.execute.return_value = execute_result
    
    client_mock = AsyncMock()
    mock_domain_client_class.return_value = client_mock
    
    await orchestrate_session_analysis(mock_session.id)
    
    assert mock_session.status == SessionStatus.completed
    client_mock.analyze_video.assert_not_called()
    client_mock.correlate_risk.assert_not_called()
