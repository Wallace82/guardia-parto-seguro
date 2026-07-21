"""
GuardIA — Risk Correlation Domain Service
"""
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.calculators.iga_calculator import calculate_iga, IGAInput, RiskLevel

app = FastAPI(title="GuardIA — Risk Service", version="1.0.0")

class RiskCorrelateRequest(BaseModel):
    session_id: str
    patient_id: str
    video_score: Optional[float] = None
    audio_score: Optional[float] = None
    document_score: Optional[float] = None

@app.get("/api/v1/risk/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "risk"}

@app.post("/api/v1/risk/correlate", status_code=status.HTTP_200_OK)
async def correlate(data: RiskCorrelateRequest):
    try:
        # Converter para o modelo de domínio do calculador
        domain_input = IGAInput(
            session_id=data.session_id,
            patient_id=data.patient_id,
            video_score=data.video_score,
            audio_score=data.audio_score,
            document_score=data.document_score
        )
        result = calculate_iga(domain_input)
        
        # Gerar recomendações/indicadores para compatibilidade com API_SPEC.md
        video_indicators = []
        if data.video_score is not None:
            if data.video_score >= 70:
                video_indicators = ["dor_facial_alta_confianca", "postura_defensiva"]
            else:
                video_indicators = ["expressao_neutra"]

        audio_indicators = []
        if data.audio_score is not None:
            if data.audio_score >= 50:
                audio_indicators = ["verbalizacao_dor", "sentimento_negativo_alto"]
            else:
                audio_indicators = ["sentimento_neutro"]

        doc_indicators = []
        if data.document_score is not None:
            if data.document_score <= 40:
                doc_indicators = ["consentimento_ausente"]
            else:
                doc_indicators = ["prontuario_regular"]

        return {
            "session_id": result.session_id,
            "iga_score": result.iga_score,
            "risk_level": result.risk_level.value,
            "calculation": {
                "video_contribution": result.video_contribution,
                "audio_contribution": result.audio_contribution,
                "document_contribution": result.document_contribution,
                "weights_applied": result.weights_applied
            },
            "justifications": {
                "video": {
                    "text": f"Detecção de vídeo retornou score de {data.video_score}.",
                    "key_indicators": video_indicators,
                    "recommendation": "Revisar abordagem durante procedimentos" if data.video_score and data.video_score >= 70 else "Nenhuma ação requerida"
                },
                "audio": {
                    "text": f"Análise de áudio retornou score de {data.audio_score}.",
                    "key_indicators": audio_indicators,
                    "recommendation": "Verificar adequação de analgesia" if data.audio_score and data.audio_score >= 50 else "Nenhuma ação requerida"
                },
                "document": {
                    "text": f"Análise de prontuário retornou score de {data.document_score}.",
                    "key_indicators": doc_indicators,
                    "recommendation": "Regularizar documentação de consentimento" if data.document_score and data.document_score <= 40 else "Nenhuma ação requerida"
                }
            },
            "calculated_at": datetime_now_iso()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def datetime_now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
