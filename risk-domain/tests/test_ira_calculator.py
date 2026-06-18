"""
Tests — IRA Calculator
Cobertura dos casos de cálculo do IRA com todos os cenários das RNs
"""
import pytest
from app.calculators.ira_calculator import (
    IRAInput,
    IRAResult,
    RiskLevel,
    calculate_ira,
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
        """IRA com todos os scores baixos deve ser classificado como BAIXO."""
        data = IRAInput(**base_session, video_score=10.0, audio_score=15.0, document_score=20.0)
        result = calculate_ira(data)

        assert result.risk_level == RiskLevel.BAIXO
        assert result.ira_score < THRESHOLD_MODERATE
        assert result.video_contribution is not None
        assert result.audio_contribution is not None
        assert result.document_contribution is not None

    def test_ira_all_components_moderate_risk(self, base_session):
        """IRA composto moderado."""
        data = IRAInput(**base_session, video_score=50.0, audio_score=45.0, document_score=40.0)
        result = calculate_ira(data)

        assert result.risk_level == RiskLevel.MODERADO
        assert THRESHOLD_MODERATE <= result.ira_score < THRESHOLD_CRITICAL

    def test_ira_all_components_critical_risk(self, base_session):
        """IRA com scores altos deve ser CRÍTICO."""
        data = IRAInput(**base_session, video_score=90.0, audio_score=80.0, document_score=70.0)
        result = calculate_ira(data)

        assert result.risk_level == RiskLevel.CRITICO
        assert result.ira_score >= THRESHOLD_CRITICAL

    def test_ira_formula_correctness(self, base_session):
        """Verificar fórmula: vídeo*0.40 + áudio*0.35 + documento*0.25"""
        data = IRAInput(**base_session, video_score=80.0, audio_score=60.0, document_score=40.0)
        result = calculate_ira(data)

        expected = (80.0 * 0.40) + (60.0 * 0.35) + (40.0 * 0.25)
        assert abs(result.ira_score - expected) < 0.01

    def test_ira_max_score(self, base_session):
        """IRA máximo deve ser 100."""
        data = IRAInput(**base_session, video_score=100.0, audio_score=100.0, document_score=100.0)
        result = calculate_ira(data)
        assert result.ira_score == 100.0

    def test_ira_zero_score(self, base_session):
        """IRA mínimo deve ser 0."""
        data = IRAInput(**base_session, video_score=0.0, audio_score=0.0, document_score=0.0)
        result = calculate_ira(data)
        assert result.ira_score == 0.0


# ============================================================
# TESTES — COMPONENTES AUSENTES (RN-003)
# ============================================================
class TestIRAMissingComponents:
    def test_ira_video_only(self, base_session):
        """IRA com apenas vídeo deve usar 100% do peso de vídeo."""
        data = IRAInput(**base_session, video_score=75.0)
        result = calculate_ira(data)

        assert result.ira_score == 75.0
        assert result.risk_level == RiskLevel.MODERADO
        assert result.audio_contribution is None
        assert result.document_contribution is None
        assert "video" in result.calculation_notes.lower() or "componente" in result.calculation_notes.lower()

    def test_ira_audio_only(self, base_session):
        """IRA com apenas áudio."""
        data = IRAInput(**base_session, audio_score=50.0)
        result = calculate_ira(data)
        assert result.ira_score == 50.0

    def test_ira_document_only(self, base_session):
        """IRA com apenas documento."""
        data = IRAInput(**base_session, document_score=30.0)
        result = calculate_ira(data)
        assert result.ira_score == 30.0

    def test_ira_video_and_audio_only(self, base_session):
        """IRA sem documento — pesos normalizados entre vídeo e áudio."""
        data = IRAInput(**base_session, video_score=80.0, audio_score=60.0)
        result = calculate_ira(data)

        # Pesos normalizados: vídeo=0.40/0.75=0.533, áudio=0.35/0.75=0.467
        expected = (80.0 * (0.40 / 0.75)) + (60.0 * (0.35 / 0.75))
        assert abs(result.ira_score - expected) < 0.01

    def test_ira_no_scores_raises_error(self, base_session):
        """Sem nenhum score, deve lançar ValueError."""
        data = IRAInput(**base_session)
        with pytest.raises(ValueError, match="Ao menos um score"):
            calculate_ira(data)


# ============================================================
# TESTES — THRESHOLDS LIMÍTROFES
# ============================================================
class TestIRAThresholds:
    def test_threshold_moderate_lower_bound(self, base_session):
        """Score exato de 40.0 deve ser MODERADO."""
        data = IRAInput(**base_session, video_score=100.0, audio_score=0.0, document_score=0.0)
        # video_score=100 * 1.0 = 100 (único componente)
        data_exact = IRAInput(**base_session, video_score=THRESHOLD_MODERATE)
        result = calculate_ira(data_exact)
        assert result.risk_level == RiskLevel.MODERADO

    def test_threshold_critical_lower_bound(self, base_session):
        """Score exato de 70.0 deve ser CRÍTICO."""
        data = IRAInput(**base_session, video_score=THRESHOLD_CRITICAL)
        result = calculate_ira(data)
        assert result.risk_level == RiskLevel.CRITICO

    def test_score_just_below_moderate(self, base_session):
        """Score de 39.99 deve ser BAIXO."""
        data = IRAInput(**base_session, video_score=39.99)
        result = calculate_ira(data)
        assert result.risk_level == RiskLevel.BAIXO
