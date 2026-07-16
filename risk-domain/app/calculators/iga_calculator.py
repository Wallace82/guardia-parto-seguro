"""
GuardIA — IGA Calculator
Cálculo do Índice GuardIA de Atenção com pesos ponderados
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    BAIXO = "baixo"
    MODERADO = "moderado"
    CRITICO = "critico"


@dataclass
class IGAInput:
    session_id: str
    patient_id: str
    video_score: Optional[float] = None   # 0.0 – 100.0
    audio_score: Optional[float] = None   # 0.0 – 100.0
    document_score: Optional[float] = None  # 0.0 – 100.0


@dataclass
class IGAResult:
    session_id: str
    patient_id: str
    iga_score: float
    risk_level: RiskLevel
    video_contribution: Optional[float]
    audio_contribution: Optional[float]
    document_contribution: Optional[float]
    weights_applied: dict
    calculation_notes: str


# Pesos base (RN-002)
BASE_WEIGHTS = {
    "video": 0.40,
    "audio": 0.35,
    "document": 0.25,
}

# Thresholds (RN-004)
THRESHOLD_MODERATE = 40.0
THRESHOLD_CRITICAL = 70.0


def calculate_iga(data: IGAInput) -> IGAResult:
    """
    Calcula o IGA (Índice GuardIA de Atenção) com base nos scores
    parciais dos domínios de vídeo, áudio e documentos.

    Aplica regras de normalização de peso quando algum componente
    está ausente (RN-003).

    Args:
        data: IGAInput com os scores parciais disponíveis.

    Returns:
        IGAResult com o score final, nível de risco e contribuições.
    """
    available = {}
    if data.video_score is not None:
        available["video"] = data.video_score
    if data.audio_score is not None:
        available["audio"] = data.audio_score
    if data.document_score is not None:
        available["document"] = data.document_score

    if not available:
        raise ValueError("Ao menos um score deve estar disponível para calcular o IGA")

    # Calcular pesos normalizados para os componentes disponíveis
    total_base_weight = sum(BASE_WEIGHTS[k] for k in available.keys())
    normalized_weights = {k: BASE_WEIGHTS[k] / total_base_weight for k in available.keys()}

    # Calcular contribuições e IGA
    contributions = {k: available[k] * normalized_weights[k] for k in available.keys()}
    iga_score = sum(contributions.values())
    iga_score = max(0.0, min(100.0, round(iga_score, 2)))

    # Classificar nível de risco
    if iga_score >= THRESHOLD_CRITICAL:
        risk_level = RiskLevel.CRITICO
    elif iga_score >= THRESHOLD_MODERATE:
        risk_level = RiskLevel.MODERADO
    else:
        risk_level = RiskLevel.BAIXO

    # Nota sobre normalização
    if len(available) < 3:
        missing = set(BASE_WEIGHTS.keys()) - set(available.keys())
        note = f"Score calculado sem: {', '.join(missing)}. Pesos normalizados para {len(available)} componente(s)."
    else:
        note = "Score calculado com todos os 3 componentes."

    return IGAResult(
        session_id=data.session_id,
        patient_id=data.patient_id,
        iga_score=iga_score,
        risk_level=risk_level,
        video_contribution=contributions.get("video"),
        audio_contribution=contributions.get("audio"),
        document_contribution=contributions.get("document"),
        weights_applied=normalized_weights,
        calculation_notes=note,
    )


def classify_risk(score: float) -> RiskLevel:
    """Classifica um score numérico no nível de risco correspondente."""
    if score >= THRESHOLD_CRITICAL:
        return RiskLevel.CRITICO
    elif score >= THRESHOLD_MODERATE:
        return RiskLevel.MODERADO
    return RiskLevel.BAIXO
