import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Garante que o diretório 'app' está no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.s3_service import s3_service
from app.services.transcribe_service import transcribe_service
from app.services.comprehend_service import comprehend_service
from app.services.textract_service import textract_service

@pytest.fixture(autouse=True)
def mock_aioboto3_session():
    mock_session = MagicMock()
    
    # Injeta o mock nas instâncias já criadas dos serviços
    s3_service.session = mock_session
    transcribe_service.session = mock_session
    comprehend_service.session = mock_session
    textract_service.session = mock_session
    
    # Também patcha a classe para importações futuras
    with patch("aioboto3.Session", return_value=mock_session):
        yield mock_session
