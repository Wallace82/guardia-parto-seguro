import pytest
import os
import cv2
from unittest.mock import patch, MagicMock
from app.services.processor import VideoProcessor

def test_process_video_file_not_found():
    processor = VideoProcessor()
    processor.process_video("session-123", "file:///shared_media/non_existent.mp4")
    
    result = processor.get_result("session-123")
    assert result is not None
    assert result["status"] == "failed"
    assert "não encontrado" in result["error"].lower()

@patch("app.services.processor.os.path.exists")
@patch("app.services.processor.cv2.VideoCapture")
def test_process_video_success(mock_cv2, mock_exists):
    # Setup mocks
    mock_exists.return_value = True
    
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.get.side_effect = lambda prop: 300 if prop == cv2.CAP_PROP_FRAME_COUNT else (30 if prop == cv2.CAP_PROP_FPS else 0)
    mock_cap.read.return_value = (True, MagicMock(shape=(1080, 1920, 3)))
    
    mock_cv2.return_value = mock_cap
    
    processor = VideoProcessor()
    
    # Executa com um blob mockado (usando patch de sleep para acelerar)
    with patch("app.services.processor.time.sleep", return_value=None):
        processor.process_video("session-456", "file:///shared_media/real_video.mp4")
        
    result = processor.get_result("session-456")
    
    assert result is not None
    assert result["status"] == "completed"
    assert result["ira_score"] == 58.9
    assert result["total_frames"] == 300
    assert result["analyzed_frames"] == 10
    
    # Verifica o caminho resolvido
    mock_cv2.assert_called_once_with("/shared_media/real_video.mp4")
