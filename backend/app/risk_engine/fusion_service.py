import structlog
from typing import List, Dict, Any

log = structlog.get_logger(__name__)

class RiskFusionEngine:
    """
    Motor de Fusão de IA
    Responsável por consolidar os resultados granulares (Vídeo, Áudio, Documento)
    em um índice de risco único (SessionRiskScore).
    """

    # Pesos padrão baseados nas variáveis de ambiente da aplicação original
    WEIGHT_VIDEO = 0.35
    WEIGHT_AUDIO = 0.30
    WEIGHT_DOCUMENT = 0.20
    WEIGHT_NOTES = 0.15

    @classmethod
    def calculate_session_risk(
        cls, 
        video_analyses: List[Any], 
        audio_analyses: List[Any], 
        document_analyses: List[Any],
        notes: str | None = None
    ) -> Dict[str, Any]:
        """
        Recebe as análises brutas e gera o score consolidado.
        Os parâmetros de entrada são instâncias dos modelos SQLAlchemy.
        """
        
        score_video = 0.0
        if video_analyses:
            # Em um cenário real, poderíamos tirar a média ou o pior caso. 
            # Para simplificar, pegamos o último ou a média do score de emoção e ansiedade.
            # Vamos simular um agregado onde anxiety/emotion contribui para o risco.
            # Supondo que `emotion_score` 100 seja algo bom ou ruim dependendo da regra.
            # Vamos assumir que os scores já representam risco (0-100).
            scores = [
                va.emotion_score for va in video_analyses 
                if va.emotion_score is not None
            ]
            if scores:
                score_video = sum(scores) / len(scores)

        score_audio = 0.0
        if audio_analyses:
            scores = [
                aa.anxiety_score for aa in audio_analyses 
                if aa.anxiety_score is not None
            ]
            if scores:
                score_audio = sum(scores) / len(scores)

        score_document = 0.0
        if document_analyses:
            scores = [
                da.clinical_risk_score for da in document_analyses 
                if da.clinical_risk_score is not None
            ]
            if scores:
                score_document = sum(scores) / len(scores)
                
        # Correlação Transmodal (Cross-modal correlation)
        # Regra solicitada: Se o áudio detecta um risco alto/agressivo, o cenário todo é de risco.
        # Portanto, o score do vídeo deve subir para se equiparar à gravidade revelada pelo áudio.
        # Porém, se o áudio for tranquilo, o vídeo MANTÉM seus critérios originais (violência silenciosa).
        if score_audio >= 60.0 and score_video > 0.0:
            if score_video < score_audio:
                # Puxa o risco do vídeo fortemente (iguala ou chega muito perto)
                score_video = score_audio
                
        # Consolidado
        total_weight = 0.0
        final_score = 0.0
        
        if score_video > 0:
            final_score += score_video * cls.WEIGHT_VIDEO
            total_weight += cls.WEIGHT_VIDEO
            
        if score_audio > 0:
            final_score += score_audio * cls.WEIGHT_AUDIO
            total_weight += cls.WEIGHT_AUDIO
            
        if score_document > 0:
            final_score += score_document * cls.WEIGHT_DOCUMENT
            total_weight += cls.WEIGHT_DOCUMENT
            
        score_notes = 0.0
        if notes:
            score_notes = cls._evaluate_notes(notes)
            if score_notes > 0:
                final_score += score_notes * cls.WEIGHT_NOTES
                total_weight += cls.WEIGHT_NOTES
            
        # Normaliza caso não tenhamos todas as fontes
        if total_weight > 0:
            global_score = round(final_score / total_weight, 2)
        else:
            global_score = 0.0
            
        # Classificação do Risco
        if global_score < 40.0:
            risk_level = "LOW"
        elif global_score < 70.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        log.info(
            "risk_engine.fusion.completed", 
            global_score=global_score, 
            level=risk_level
        )

        return {
            "globalScore": global_score,
            "riskLevel": risk_level,
            "sources": {
                "video": round(score_video, 2) if score_video > 0 else None,
                "audio": round(score_audio, 2) if score_audio > 0 else None,
                "document": round(score_document, 2) if score_document > 0 else None,
                "notes": round(score_notes, 2) if score_notes > 0 else None
            }
        }

    @classmethod
    def _evaluate_notes(cls, notes: str) -> float:
        """Avaliação inteligente das anotações clínicas usando OpenAI."""
        import os
        import openai
        import json
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or not notes.strip():
            log.warning("openai_notes_fallback", reason="Sem API KEY ou sem anotações")
            # Fallback (Regex antigo)
            text = notes.lower()
            risk_keywords = ["ansiedade", "medo", "dor", "tensão", "receio", "insegurança", "risco", "sangramento", "preocupação", "alteração", "desconforto", "choro", "taquicardia", "hipertensão", "desespero", "sofrimento", "hemorragia"]
            positive_keywords = ["tranquila", "calma", "sem queixas", "estável", "boa", "confortável", "sorridente", "cooperativa", "aliviada", "relaxada", "segura", "repouso", "sem alterações", "sem dor"]
            
            score = 50.0
            for kw in risk_keywords:
                if kw in text: score += 15.0
            for kw in positive_keywords:
                if kw in text: score -= 10.0
            return min(max(score, 0.0), 100.0)
            
        try:
            client = openai.OpenAI(api_key=api_key)
            prompt = f"""
Você é um auditor médico especialista. Leia as seguintes anotações clínicas de um atendimento obstétrico e avalie o risco do paciente.
O risco varia de 0 (perfeitamente estável, relaxada, sem dores) a 100 (risco crítico, dor extrema, complicações).

Anotações Clínicas: "{notes}"

Retorne um JSON estritamente neste formato:
{{
  "risk_score": valor numerico de 0 a 100
}}
"""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" },
                temperature=0.1
            )
            data_json = json.loads(response.choices[0].message.content)
            score = float(data_json.get("risk_score", 50.0))
            log.info("openai_notes_success", score=score)
            return min(max(score, 0.0), 100.0)
        except Exception as oai_err:
            log.error("openai_notes_failed", error=str(oai_err))
            return 50.0
