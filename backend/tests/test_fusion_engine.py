import pytest
from app.risk_engine.fusion_service import RiskFusionEngine

class MockAnalysis:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_fusion_engine_case1_low_risk():
    """
    Caso 1: Vídeo positivo, Áudio positivo, Documento normal
    Resultado esperado: Baixo risco
    """
    videos = [MockAnalysis(emotion_score=20.0)]
    audios = [MockAnalysis(anxiety_score=15.0)]
    docs = [MockAnalysis(clinical_risk_score=10.0)]
    
    result = RiskFusionEngine.calculate_session_risk(videos, audios, docs)
    
    assert result["globalScore"] < 40.0
    assert result["riskLevel"] == "LOW"

def test_fusion_engine_case2_high_risk():
    """
    Caso 2: Vídeo com ansiedade, Áudio negativo, Documento crítico
    Resultado esperado: Alto risco
    """
    videos = [MockAnalysis(emotion_score=80.0)]
    audios = [MockAnalysis(anxiety_score=85.0)]
    docs = [MockAnalysis(clinical_risk_score=90.0)]
    
    result = RiskFusionEngine.calculate_session_risk(videos, audios, docs)
    
    assert result["globalScore"] > 70.0
    assert result["riskLevel"] == "HIGH"

def test_fusion_engine_empty_sources():
    """
    Caso: Nenhuma análise disponível
    Resultado esperado: Score 0, Baixo risco
    """
    result = RiskFusionEngine.calculate_session_risk([], [], [])
    
    assert result["globalScore"] == 0.0
    assert result["riskLevel"] == "LOW"
    assert result["sources"]["video"] is None
