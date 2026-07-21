"""
GuardIA — Video Domain — Testes do Processador de Vídeo

Testes unitários para o VideoProcessor com mocks de OpenCV.
"""
import pytest
import os
import cv2
from unittest.mock import patch, MagicMock
from app.services.processor import VideoProcessor


class TestVideoProcessorFileNotFound:
    """Testes para cenários de arquivo não encontrado."""

    def test_process_video_file_not_found(self):
        """Verifica que arquivo inexistente resulta em status 'failed'."""
        processor = VideoProcessor()
        processor.process_video("session-123", "session-123", "file:///shared_media/non_existent.mp4")

        result = processor.get_result("session-123")
        assert result is not None
        assert result["status"] == "failed"
        assert "não encontrado" in result["error"].lower()

    def test_process_video_file_url_resolution(self):
        """Verifica que o processador resolve corretamente URLs file://."""
        processor = VideoProcessor()
        # Arquivo não existe, mas testa a resolução do caminho
        processor.process_video("session-url-test", "session-url-test", "file:///shared_media/test.mp4")
        result = processor.get_result("session-url-test")
        assert result["status"] == "failed"


class TestVideoProcessorSuccess:
    """Testes para cenários de processamento bem-sucedido."""

    @patch("app.services.processor.os.path.exists")
    @patch("app.services.processor.cv2.VideoCapture")
    def test_process_video_success(self, mock_cv2, mock_exists):
        """Verifica processamento completo com mocks de OpenCV."""
        # Setup mocks
        mock_exists.return_value = True

        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = (
            lambda prop: 300
            if prop == cv2.CAP_PROP_FRAME_COUNT
            else (30 if prop == cv2.CAP_PROP_FPS else 0)
        )
        mock_cap.read.return_value = (True, MagicMock(shape=(1080, 1920, 3)))
        mock_cv2.return_value = mock_cap

        processor = VideoProcessor()

        with patch("app.services.processor.time.sleep", return_value=None):
            processor.process_video(
                "session-456", "session-456", "file:///shared_media/real_video.mp4"
            )

        result = processor.get_result("session-456")

        assert result is not None
        assert result["status"] == "completed"
        assert result["session_id"] == "session-456"
        assert 45.0 <= result["iga_score"] <= 85.0
        assert result["total_frames"] == 300
        assert result["analyzed_frames"] == 10
        assert "components" in result
        assert "emotion_score" in result["components"]
        assert "pose_score" in result["components"]
        assert "object_risk_score" in result["components"]
        assert "bleeding_score" in result["components"]
        assert "key_findings" in result
        assert "completed_at" in result

        # Verifica o caminho resolvido
        mock_cv2.assert_called_once_with("/shared_media/real_video.mp4")

    @patch("app.services.processor.os.path.exists")
    @patch("app.services.processor.cv2.VideoCapture")
    def test_process_video_deterministic_score(self, mock_cv2, mock_exists):
        """Verifica que o mesmo arquivo gera o mesmo score (determinismo)."""
        mock_exists.return_value = True

        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = (
            lambda prop: 300
            if prop == cv2.CAP_PROP_FRAME_COUNT
            else (30 if prop == cv2.CAP_PROP_FPS else 0)
        )
        mock_cap.read.return_value = (True, MagicMock(shape=(720, 1280, 3)))
        mock_cv2.return_value = mock_cap

        processor = VideoProcessor()

        with patch("app.services.processor.time.sleep", return_value=None):
            processor.process_video("s1", "s1", "file:///shared_media/test.mp4")
            # Limpa o resultado para a segunda execução
            score1 = processor.get_result("s1")["iga_score"]

        # Reseta mocks
        mock_cv2.reset_mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = (
            lambda prop: 300
            if prop == cv2.CAP_PROP_FRAME_COUNT
            else (30 if prop == cv2.CAP_PROP_FPS else 0)
        )
        mock_cap.read.return_value = (True, MagicMock(shape=(720, 1280, 3)))
        mock_cv2.return_value = mock_cap

        with patch("app.services.processor.time.sleep", return_value=None):
            processor.process_video("s2", "s2", "file:///shared_media/test.mp4")
            score2 = processor.get_result("s2")["iga_score"]

        assert score1 == score2  # Mesmo arquivo = mesmo score

    @patch("app.services.processor.os.path.exists")
    @patch("app.services.processor.cv2.VideoCapture")
    def test_process_video_opencv_failure(self, mock_cv2, mock_exists):
        """Verifica que falha do OpenCV resulta em status 'failed'."""
        mock_exists.return_value = True

        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False  # Simula falha ao abrir
        mock_cv2.return_value = mock_cap

        processor = VideoProcessor()
        processor.process_video("session-fail", "session-fail", "file:///shared_media/corrupt.mp4")

        result = processor.get_result("session-fail")
        assert result is not None
        assert result["status"] == "failed"
        assert "error" in result


class TestVideoProcessorGetResult:
    """Testes para o método get_result."""

    def test_get_result_nonexistent(self):
        """Verifica que sessão inexistente retorna None."""
        processor = VideoProcessor()
        result = processor.get_result("nonexistent")
        assert result is None
