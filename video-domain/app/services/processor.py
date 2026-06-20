import os
import cv2
import time
import structlog
from datetime import datetime, timezone
from app.core.config import settings

log = structlog.get_logger(__name__)

# Simulação de um banco de dados em memória para os resultados
_RESULTS_DB = {}

class VideoProcessor:
    
    def process_video(self, session_id: str, blob_url: str):
        """
        Lê o arquivo do volume local (removendo file:///)
        e processa os frames.
        """
        log.info("starting_video_processing", session_id=session_id, blob_url=blob_url)
        
        # 1. Traduzir URL para caminho local
        file_path = blob_url
        if blob_url.startswith("file:///"):
            file_path = blob_url.replace("file:///", "/")
        elif blob_url.startswith("file://"):
            file_path = blob_url.replace("file://", "")
            
        # Para ambiente Windows rodando local sem Docker (fallback de testes)
        if os.name == 'nt' and file_path.startswith('/C:'):
            file_path = file_path[1:]
            
        log.info("local_file_path_resolved", file_path=file_path)
        
        # 2. Verificar se o arquivo existe
        if not os.path.exists(file_path):
            log.error("file_not_found", file_path=file_path)
            _RESULTS_DB[session_id] = {
                "status": "failed",
                "error": "Arquivo não encontrado no volume compartilhado"
            }
            return

        # 3. Processamento via OpenCV
        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                raise ValueError("Não foi possível abrir o vídeo com OpenCV")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration_seconds = total_frames / fps if fps > 0 else 0
            
            log.info("video_opened", total_frames=total_frames, fps=fps, duration=duration_seconds)
            
            # Lê apenas o primeiro frame como prova de conceito
            ret, frame = cap.read()
            if ret:
                height, width, _ = frame.shape
                log.info("first_frame_read_success", resolution=f"{width}x{height}")
            
            cap.release()
            
            # Aqui entraríamos com DeepFace/YOLO.
            # Para manter a demonstração rápida, preenchemos resultados simulados.
            # No futuro, um loop leria frame a frame (1 por segundo).
            
            # Simula tempo de processamento de rede/IA
            time.sleep(2)
            
            _RESULTS_DB[session_id] = {
                "session_id": session_id,
                "status": "completed",
                "ira_score": 68.4,
                "components": {
                    "emotion_score": 75.2,
                    "pose_score": 60.1,
                    "object_risk_score": 45.0,
                    "bleeding_score": 0.0
                },
                "total_frames": total_frames,
                "analyzed_frames": 1,
                "key_findings": [
                    {
                        "type": "emotion",
                        "timestamp_seconds": duration_seconds / 2 if duration_seconds > 0 else 0,
                        "description": "Expressão de dor detectada com confiança 0.89",
                        "confidence": 0.89
                    }
                ],
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            log.info("video_processing_completed", session_id=session_id)
            
        except Exception as e:
            log.exception("video_processing_failed", session_id=session_id, error=str(e))
            _RESULTS_DB[session_id] = {
                "status": "failed",
                "error": str(e)
            }

    def get_result(self, session_id: str):
        return _RESULTS_DB.get(session_id)
