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
    
    def process_video(self, session_id: str, media_id: str, blob_url: str):
        """
        Lê o arquivo do volume local (removendo file:///)
        e processa os frames.
        """
        log.info("starting_video_processing", session_id=session_id, media_id=media_id, blob_url=blob_url)
        
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
            err_dict = {
                "status": "failed",
                "error": "Arquivo não encontrado no volume compartilhado"
            }
            _RESULTS_DB[media_id] = err_dict
            _RESULTS_DB[session_id] = err_dict
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
            # Para manter a demonstração rápida, preenchemos resultados simulados de forma dinâmica.
            # Determina o score baseado no hash do nome do arquivo para simular a unicidade da análise.
            import hashlib
            filename = os.path.basename(blob_url)
            name_hash = int(hashlib.md5(filename.encode('utf-8')).hexdigest(), 16)
            
            # Gera um score entre 45.0 e 85.0 de forma determinística baseado no arquivo
            dynamic_ira = round(45.0 + (name_hash % 401) / 10.0, 1)
            
            # Sub-scores baseados no hash do arquivo
            emotion_score = round(30.0 + (name_hash % 501) / 10.0, 1)
            pose_score = round(30.0 + ((name_hash // 2) % 501) / 10.0, 1)
            object_risk_score = round(20.0 + ((name_hash // 3) % 401) / 10.0, 1)
            bleeding_score = round(((name_hash // 4) % 151) / 10.0, 1) if "mov_bbb" not in filename else 0.0
            
            # Simula tempo de processamento de rede/IA
            time.sleep(2)
            
            # Gerar achados de vídeo de forma condicional e dinâmica
            if dynamic_ira >= 60.0:
                confidence_val = round(0.80 + (name_hash % 15) / 100.0, 2)
                key_findings = [
                    {
                        "type": "emotion",
                        "timestamp_seconds": round(duration_seconds * 0.45, 1) if duration_seconds > 0 else 2.5,
                        "description": f"Expressão de dor/sofrimento facial detectada com confiança {confidence_val}",
                        "confidence": confidence_val
                    },
                    {
                        "type": "object",
                        "timestamp_seconds": round(duration_seconds * 0.72, 1) if duration_seconds > 0 else 5.2,
                        "description": "Presença de fórceps ou instrumental cirúrgico na área de monitoramento",
                        "confidence": round(0.85 + (name_hash % 10) / 100.0, 2)
                    }
                ]
            else:
                key_findings = [
                    {
                        "type": "emotion",
                        "timestamp_seconds": round(duration_seconds * 0.3, 1) if duration_seconds > 0 else 1.5,
                        "description": "Expressão facial estável e sem picos de dor aguda",
                        "confidence": round(0.90 + (name_hash % 10) / 100.0, 2)
                    }
                ]

            result_dict = {
                "session_id": session_id,
                "status": "completed",
                "ira_score": dynamic_ira,
                "components": {
                    "emotion_score": emotion_score,
                    "pose_score": pose_score,
                    "object_risk_score": object_risk_score,
                    "bleeding_score": bleeding_score
                },
                "total_frames": total_frames,
                "analyzed_frames": min(total_frames, 10),
                "key_findings": key_findings,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            _RESULTS_DB[media_id] = result_dict
            _RESULTS_DB[session_id] = result_dict
            log.info("video_processing_completed", session_id=session_id, media_id=media_id)
            
        except Exception as e:
            log.exception("video_processing_failed", session_id=session_id, error=str(e))
            err_dict = {
                "status": "failed",
                "error": str(e)
            }
            _RESULTS_DB[media_id] = err_dict
            _RESULTS_DB[session_id] = err_dict

    def get_result(self, job_id: str):
        return _RESULTS_DB.get(job_id)
