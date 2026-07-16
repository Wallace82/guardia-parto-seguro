"""
GuardIA — Domain Services client
Interação via REST com os microsserviços de vídeo, áudio, documentos, risco e relatórios.
"""
import httpx
import structlog
from typing import Optional, Dict, Any
from app.config import settings

log = structlog.get_logger(__name__)

class DomainClient:
    """Cliente HTTP assíncrono para os microsserviços de domínio."""

    def __init__(self):
        self.timeout = httpx.Timeout(10.0, read=30.0)

    async def analyze_video(self, session_id: int, media_id: int, blob_url: str) -> Dict[str, Any]:
        """Inicia análise de vídeo no video-service."""
        url = f"{settings.VIDEO_SERVICE_URL}/api/v1/video/analyze"
        payload = {
            "session_id": str(session_id),
            "media_id": str(media_id),
            "blob_url": blob_url,
            "options": {
                "analyze_emotions": True,
                "analyze_pose": True,
                "detect_objects": True,
                "detect_bleeding": True,
                "frame_sample_rate": settings.VIDEO_FRAME_SAMPLE_RATE
            }
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log.info("video_analyze_request", url=url, session_id=session_id)
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_video_results(self, job_id: str | int) -> Dict[str, Any]:
        """Obtém resultados da análise de vídeo."""
        url = f"{settings.VIDEO_SERVICE_URL}/api/v1/video/results/{job_id}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log.info("video_results_request", url=url, job_id=job_id)
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def analyze_audio(self, session_id: int, media_id: int, blob_url: str) -> Dict[str, Any]:
        """Inicia análise de áudio no audio-service."""
        url = f"{settings.AUDIO_SERVICE_URL}/api/v1/audio/analyze"
        payload = {
            "session_id": str(session_id),
            "media_id": str(media_id),
            "blob_url": blob_url,
            "options": {
                "speaker_diarization": True,
                "sentiment_analysis": True,
                "ner_extraction": True,
                "risk_keyword_detection": True
            }
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log.info("audio_analyze_request", url=url, session_id=session_id)
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_audio_results(self, job_id: str | int) -> Dict[str, Any]:
        """Obtém resultados da análise de áudio."""
        url = f"{settings.AUDIO_SERVICE_URL}/api/v1/audio/results/{job_id}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log.info("audio_results_request", url=url, job_id=job_id)
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def analyze_document(self, session_id: int, media_id: int, blob_url: str) -> Dict[str, Any]:
        """Processa documento médico no document-service (retorna resultado diretamente)."""
        url = f"{settings.DOCUMENT_SERVICE_URL}/api/v1/documents/analyze"
        payload = {
            "session_id": str(session_id),
            "media_id": str(media_id),
            "blob_url": blob_url,
            "document_type": "prontuario"
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log.info("document_analyze_request", url=url, session_id=session_id)
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def analyze_notes(self, session_id: int, notes: str) -> Dict[str, Any]:
        """Envia as anotações textuais da sessão para análise no document-service."""
        url = f"{settings.DOCUMENT_SERVICE_URL}/api/v1/documents/analyze-notes"
        payload = {
            "session_id": str(session_id),
            "notes": notes
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log.info("document_analyze_notes_request", url=url, session_id=session_id)
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def correlate_risk(
        self,
        session_id: int,
        patient_code: str,
        video_score: Optional[float] = None,
        audio_score: Optional[float] = None,
        document_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calcula o IGA Composto no risk-service."""
        url = f"{settings.RISK_SERVICE_URL}/api/v1/risk/correlate"
        payload = {
            "session_id": str(session_id),
            "patient_id": patient_code or "unknown", # patient_code é o ID anonimizado
            "video_score": video_score,
            "audio_score": audio_score,
            "document_score": document_score
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log.info("risk_correlate_request", url=url, session_id=session_id, scores={
                "video": video_score, "audio": audio_score, "document": document_score
            })
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def generate_report(self, session_id: int) -> Dict[str, Any]:
        """Gera o relatório da sessão no report-service."""
        url = f"{settings.REPORT_SERVICE_URL}/api/v1/reports/generate"
        payload = {
            "session_id": str(session_id),
            "report_type": "session",
            "report_format": "pdf",
            "include_transcription": True,
            "include_key_frames": True
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log.info("report_generate_request", url=url, session_id=session_id)
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
