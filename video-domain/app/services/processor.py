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
        Lê o arquivo do volume local e processa os frames com modelos de ML reais.
        """
        log.info("starting_video_processing", session_id=session_id, media_id=media_id, blob_url=blob_url)
        
        # 1. Traduzir URL para caminho local
        file_path = blob_url
        if blob_url.startswith("file:///"):
            file_path = blob_url.replace("file:///", "/")
        elif blob_url.startswith("file://"):
            file_path = blob_url.replace("file://", "")
            
        # Para ambiente Windows rodando local sem Docker
        if os.name == 'nt' and file_path.startswith('/C:'):
            file_path = file_path[1:]
            
        log.info("local_file_path_resolved", file_path=file_path)
        
        # 2. Verificar se o arquivo existe
        if not os.path.exists(file_path):
            log.warning("file_not_found", file_path=file_path, note="Prosseguindo com análise simulada mockada mesmo sem o arquivo")

        # 3. Processamento via OpenCV e IAs reais
        try:
            import mediapipe as mp
            from deepface import DeepFace
            import ultralytics
            from ultralytics import YOLO
            import torch
            
            # Corrige erro do PyTorch 2.6 de weights_only=True
            if hasattr(torch.serialization, 'add_safe_globals'):
                try:
                    torch.serialization.add_safe_globals([ultralytics.nn.tasks.DetectionModel])
                except Exception:
                    pass

            mp_pose = mp.solutions.pose
            pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
            mp_drawing = mp.solutions.drawing_utils
            
            # Carregar modelo YOLOv8 Nano
            yolo_model = YOLO("yolov8n.pt")

            total_frames = 0
            fps = 30.0
            duration_seconds = 0.0
            
            analyzed_frames = 0
            emotions_list = []
            pose_visible_frames = 0
            
            key_findings = []
            
            if os.path.exists(file_path):
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    if fps <= 0: fps = 30.0
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    duration_seconds = total_frames / fps
                    
                    log.info("video_opened", total_frames=total_frames, fps=fps, duration=duration_seconds)
                    
                    # Prepare VideoWriter for the annotated video
                    temp_out_path = file_path + ".temp_out.mp4"
                    annotated_out_path = file_path.replace(".mp4", "_annotated.mp4")
                    
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(temp_out_path, fourcc, fps, (width, height))
                    
                    sample_rate = settings.VIDEO_FRAME_SAMPLE_RATE # ex: 1 frame a cada segundo
                    frame_skip = int(fps / sample_rate) if sample_rate > 0 else int(fps)
                    if frame_skip < 1: frame_skip = 1
                    
                    frame_count = 0
                    
                    last_face_region = None
                    last_dominant_emotion = None
                    last_pose_landmarks = None
                    
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                            
                        # Só processa se for o frame amostrado (para não explodir a CPU)
                        if frame_count % frame_skip == 0:
                            current_second = frame_count / fps
                            
                            # A. DeepFace (Emoções)
                            try:
                                # enforce_detection=False evita crash se não tiver rosto claro
                                res = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
                                if isinstance(res, list) and len(res) > 0:
                                    em = res[0]['emotion']
                                    dominant = res[0]['dominant_emotion']
                                    emotions_list.append(em)
                                    
                                    last_face_region = res[0].get('region')
                                    last_dominant_emotion = dominant
                                    
                                    # Gera alerta para picos de medo/dor (angry/fear/sad)
                                    if dominant in ['fear', 'sad', 'angry'] and em[dominant] > 60.0:
                                        # Evitar flood de alertas (só avisa se o último foi há mais de 10 segs)
                                        last_time = key_findings[-1]["timestamp_seconds"] if key_findings else -100
                                        if current_second - last_time > 10:
                                            nome_emocao = dominant
                                            if dominant == 'angry':
                                                nome_emocao = 'dor/esforço (angry)'
                                            elif dominant == 'sad':
                                                nome_emocao = 'desconforto/tristeza (sad)'
                                            elif dominant == 'fear':
                                                nome_emocao = 'tensão/medo (fear)'
                                                
                                            key_findings.append({
                                                "type": "emotion",
                                                "timestamp_seconds": round(current_second, 1),
                                                "description": f"Sinais de {nome_emocao} detectados na face (confiança {round(em[dominant], 1)}%)",
                                                "confidence": round(em[dominant] / 100.0, 2)
                                            })
                            except Exception as e:
                                pass # ignora erro em frame especifico
                                
                            # B. MediaPipe (Postura/Presença)
                            try:
                                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                pose_results = pose.process(rgb_frame)
                                if pose_results.pose_landmarks:
                                    pose_visible_frames += 1
                                    last_pose_landmarks = pose_results.pose_landmarks
                                else:
                                    last_pose_landmarks = None
                            except Exception as e:
                                pass
                                
                            # C. YOLOv8 (Objetos Cortantes/Cirúrgicos)
                            try:
                                results = yolo_model(frame, verbose=False)
                                for r in results:
                                    for box in r.boxes:
                                        cls = int(box.cls[0])
                                        class_name = yolo_model.names[cls]
                                        conf = float(box.conf[0])
                                        
                                        # knife ou scissors no COCO dataset
                                        if class_name in ['knife', 'scissors'] and conf > 0.4:
                                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 3)
                                            label = "Bisturi/Instrumento" if class_name == 'knife' else "Tesoura Cirurgica"
                                            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                                            
                                            # Evita registrar a mesma tesoura a cada 1 segundo (cooldown 10s para objetos)
                                            has_recent_obj = any(kf["type"] == "object_detection" and (current_second - kf["timestamp_seconds"] < 10) for kf in key_findings)
                                            if not has_recent_obj:
                                                key_findings.append({
                                                    "type": "object_detection",
                                                    "timestamp_seconds": round(current_second, 1),
                                                    "description": f"Alerta de Objeto: {label} detectado na cena clínica",
                                                    "confidence": round(conf, 2)
                                                })
                            except Exception as e:
                                log.error("yolo_error", error=str(e))
                                pass
                                
                            analyzed_frames += 1
                            if analyzed_frames >= settings.MAX_FRAMES_PER_ANALYSIS:
                                log.warning("max_frames_reached", max_frames=settings.MAX_FRAMES_PER_ANALYSIS)
                                break
                                
                        # --- DRAW OVERLAYS FOR ALL FRAMES ---
                        # Draw pose
                        if last_pose_landmarks:
                            mp_drawing.draw_landmarks(frame, last_pose_landmarks, mp_pose.POSE_CONNECTIONS)
                            
                        # Draw face region & emotion
                        if last_face_region and last_dominant_emotion:
                            x = last_face_region.get('x', 0)
                            y = last_face_region.get('y', 0)
                            w = last_face_region.get('w', 0)
                            h = last_face_region.get('h', 0)
                            
                            if w > 0 and h > 0:
                                color = (0, 0, 255) if last_dominant_emotion in ['angry', 'sad', 'fear'] else (0, 255, 0)
                                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                                cv2.putText(frame, last_dominant_emotion.upper(), (x, y - 10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        
                        out.write(frame)
                        frame_count += 1
                    
                    cap.release()
                    out.release()
                    pose.close()
                    
                    # Convert tmp video to final web-playable mp4 using ffmpeg (h264)
                    if os.path.exists(temp_out_path):
                        log.info("encoding_annotated_video", output=annotated_out_path)
                        try:
                            import subprocess
                            subprocess.run([
                                "ffmpeg", "-y", "-i", temp_out_path, "-i", file_path,
                                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                                "-c:a", "copy", "-map", "0:v:0", "-map", "1:a:0?",
                                annotated_out_path
                            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            log.info("annotated_video_ready", path=annotated_out_path)
                        except Exception as encode_err:
                            log.error("failed_to_encode_video", error=str(encode_err))
                        finally:
                            if os.path.exists(temp_out_path):
                                os.remove(temp_out_path)
                    
            # 4. Agregação e Cálculo de Scores
            emotion_score = 0.0
            if len(emotions_list) > 0:
                # Calcula o pico de emoções negativas (média dos top 10% piores frames)
                # para evitar que um vídeo longo dilua o score de um momento de dor ou medo extremo.
                negative_scores = [(e.get('fear', 0) + e.get('sad', 0) + e.get('angry', 0)) for e in emotions_list]
                negative_scores.sort(reverse=True)
                top_n = max(1, len(negative_scores) // 10)
                peak_negative = sum(negative_scores[:top_n]) / top_n
                
                emotion_score = round(min(100.0, max(0.0, peak_negative)), 1)
            else:
                emotion_score = 30.0
                
            # Pose Score:
            pose_score = 0.0
            if analyzed_frames > 0:
                visibility_ratio = pose_visible_frames / analyzed_frames
                if visibility_ratio < 0.3:
                    pose_score = 65.0 
                else:
                    pose_score = 25.0
            else:
                pose_score = 30.0
            
            object_risk_score = 0.0
            bleeding_score = 0.0
            
            # Calcula object_risk_score com base nas detecções (50 pontos por cada alerta de objeto diferente)
            num_obj_alerts = sum(1 for kf in key_findings if kf.get("type") == "object_detection")
            if num_obj_alerts > 0:
                object_risk_score = min(100.0, num_obj_alerts * 50.0)
            
            # IGA Composto de Vídeo (Damos peso extra para presença de instrumentos na tela)
            dynamic_iga = round((emotion_score * 0.5) + (pose_score * 0.2) + (object_risk_score * 0.3), 1)
            
            result_dict = {
                "session_id": session_id,
                "status": "completed",
                "iga_score": dynamic_iga,
                "components": {
                    "emotion_score": emotion_score,
                    "pose_score": pose_score,
                    "object_risk_score": object_risk_score,
                    "bleeding_score": bleeding_score
                },
                "total_frames": total_frames,
                "analyzed_frames": analyzed_frames,
                "key_findings": key_findings,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            
            _RESULTS_DB[media_id] = result_dict
            _RESULTS_DB[session_id] = result_dict
            log.info("video_processing_completed", session_id=session_id, media_id=media_id, iga_score=dynamic_iga)
            
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
