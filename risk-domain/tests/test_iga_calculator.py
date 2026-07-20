"""
Tests — IGA Calculator
Cobertura dos casos de cálculo do IGA com todos os cenários das RNs
"""
import pytest
from app.calculators.iga_calculator import (
    IGAInput,
    IGAResult,
    RiskLevel,
    calculate_iga,
    THRESHOLD_MODERATE,
    THRESHOLD_CRITICAL,
)


# ============================================================
# FIXTURES
# ============================================================
@pytest.fixture
def base_session():
    return {"session_id": "test-session-001", "patient_id": "test-patient-001"}


# ============================================================
# TESTES — CÁLCULO COM TODOS OS COMPONENTES
# ============================================================
class TestIRACalculationAllComponents:
    def test_ira_all_components_low_risk(self, base_session):
        """IGA com todos os scores baixos deve ser classificado como BAIXO."""
        data = IGAInput(**base_session, video_score=10.0, audio_score=15.0, document_score=20.0)
        result = calculate_iga(data)

        assert result.risk_level == RiskLevel.BAIXO
        assert result.iga_score < THRESHOLD_MODERATE
        assert result.video_contribution is not None
        assert result.audio_contribution is not None
        assert result.document_contribution is not None

    def test_ira_all_components_moderate_risk(self, base_session):
        """IGA Composto moderado."""
        data = IGAInput(**base_session, video_score=50.0, audio_score=45.0, document_score=40.0)
        result = calculate_iga(data)

        assert result.risk_level == RiskLevel.MODERADO
        assert THRESHOLD_MODERATE <= result.iga_score < THRESHOLD_CRITICAL

    def test_ira_all_components_critical_risk(self, base_session):
        """IGA com scores altos deve ser CRÍTICO."""
        data = IGAInput(**base_session, video_score=90.0, audio_score=80.0, document_score=70.0)
        result = calculate_iga(data)

        assert result.risk_level == RiskLevel.CRITICO
        assert result.iga_score >= THRESHOLD_CRITICAL

    def test_ira_formula_correctness(self, base_session):
        """Verificar fórmula: vídeo*0.40 + áudio*0.35 + documento*0.25"""
        # audio = 60.0, não sofre o desconto de contexto (60 > 30)
        data = IGAInput(**base_session, video_score=80.0, audio_score=60.0, document_score=40.0)
        result = calculate_iga(data)

        expected = (80.0 * 0.40) + (60.0 * 0.35) + (40.0 * 0.25)
        assert abs(result.iga_score - expected) < 0.01

    def test_contextual_discount_on_calm_audio(self, base_session):
        """Vídeo alto com áudio baixo deve atenuar o impacto do vídeo e não gerar alerta crítico."""
        data = IGAInput(**base_session, video_score=100.0, audio_score=20.0, document_score=0.0)
        result = calculate_iga(data)

        # Regra de atenuação: vídeo cai para 0.20, áudio sobe para 0.55. Documento continua 0.25.
        # Score = (100 * 0.20) + (20 * 0.55) + (0 * 0.25) = 20 + 11 = 31
        # 31 é BAIXO
        assert abs(result.iga_score - 31.0) < 0.01
        assert result.risk_level == RiskLevel.BAIXO
        assert "Peso de vídeo atenuado" in result.calculation_notes

    def test_ira_max_score(self, base_session):
        """IGA máximo deve ser 100."""
        data = IGAInput(**base_session, video_score=100.0, audio_score=100.0, document_score=100.0)
        result = calculate_iga(data)
        assert result.iga_score == 100.0

    def test_ira_zero_score(self, base_session):
        """IGA mínimo deve ser 0."""
        data = IGAInput(**base_session, video_score=0.0, audio_score=0.0, document_score=0.0)
        result = calculate_iga(data)
        assert result.iga_score == 0.0


# ============================================================
# TESTES — COMPONENTES AUSENTES (RN-003)
# ============================================================
class TestIRAMissingComponents:
    def test_ira_video_only(self, base_session):
        """IGA com apenas vídeo deve usar 100% do peso de vídeo."""
        data = IGAInput(**base_session, video_score=75.0)
        result = calculate_iga(data)

        assert result.iga_score == 75.0
        assert result.risk_level == RiskLevel.CRITICO
        assert result.audio_contribution is None
        assert result.document_contribution is None
        assert "video" in result.calculation_notes.lower() or "componente" in result.calculation_notes.lower()

    def test_ira_audio_only(self, base_session):
        """IGA com apenas áudio."""
        data = IGAInput(**base_session, audio_score=50.0)
        result = calculate_iga(data)
        assert result.iga_score == 50.0

    def test_ira_document_only(self, base_session):
        """IGA com apenas documento."""
        data = IGAInput(**base_session, document_score=30.0)
        result = calculate_iga(data)
        assert result.iga_score == 30.0

    def test_ira_video_and_audio_only(self, base_session):
        """IGA sem documento — pesos normalizados entre vídeo e áudio."""
        data = IGAInput(**base_session, video_score=80.0, audio_score=60.0)
        result = calculate_iga(data)

        # Pesos normalizados: vídeo=0.40/0.75=0.533, áudio=0.35/0.75=0.467
        expected = (80.0 * (0.40 / 0.75)) + (60.0 * (0.35 / 0.75))
        assert abs(result.iga_score - expected) < 0.01

    def test_ira_no_scores_raises_error(self, base_session):
        """Sem nenhum score, deve lançar ValueError."""
        data = IGAInput(**base_session)
        with pytest.raises(ValueError, match="Ao menos um score"):
            calculate_iga(data)


# ============================================================
# TESTES — THRESHOLDS LIMÍTROFES
# ============================================================
class TestIRAThresholds:
    def test_threshold_moderate_lower_bound(self, base_session):
        """Score exato de 40.0 deve ser MODERADO."""
        # Se usássemos áudio=0.0 (como o comentário original sugeria), a atenuação de vídeo ocorreria.
        # Como o teste só passa video_score, não há áudio, logo não há desconto de contexto.
        data_exact = IGAInput(**base_session, video_score=THRESHOLD_MODERATE)
        result = calculate_iga(data_exact)
        assert result.risk_level == RiskLevel.MODERADO

    def test_threshold_critical_lower_bound(self, base_session):
        """Score exato de 70.0 deve ser CRÍTICO."""
        data = IGAInput(**base_session, video_score=THRESHOLD_CRITICAL)
        result = calculate_iga(data)
        assert result.risk_level == RiskLevel.CRITICO

    def test_score_just_below_moderate(self, base_session):
        """Score de 39.99 deve ser BAIXO."""
        data = IGAInput(**base_session, video_score=39.99)
        result = calculate_iga(data)
        assert result.risk_level == RiskLevel.BAIXO
