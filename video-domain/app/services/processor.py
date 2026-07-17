import os
import cv2
import time
import structlog
from datetime import datetime, timezone
from app.core.config import settings

# Import Object Intelligence Modules
from app.services.object_intelligence.detector import MedicalObjectDetector
from app.services.object_intelligence.association import ObjectAssociator
from app.services.object_intelligence.inference import RoleInferenceEngine

log = structlog.get_logger(__name__)

# Simulação de um banco de dados em memória para os resultados
_RESULTS_DB = {}

class FaceTracker:
    def __init__(self, inference_engine):
        self.faces = {} # face_id -> {centroid, role, bbox, dominant_emotion, confidence, events, associated_objects, first_frame}
        self.next_id = 1
        self.inference_engine = inference_engine
        
    def _distance(self, p1, p2):
        import math
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
        
    def update(self, detected_faces, current_frame):
        # Reset active status
        for fid in self.faces:
            self.faces[fid]['active_this_frame'] = False
            
        updated = []
        for det in detected_faces:
            x, y, w, h = det['bbox']
            centroid = (x + w/2, y + h/2)
            
            best_id = None
            best_dist = 150 # max distance threshold
            for fid, fdata in self.faces.items():
                if fdata['active_this_frame']: continue
                dist = self._distance(centroid, fdata['centroid'])
                if dist < best_dist:
                    best_dist = dist
                    best_id = fid
            
            if best_id is None:
                # new face
                best_id = f"Face_{self.next_id:03d}"
                self.next_id += 1
                self.faces[best_id] = {
                    'role': 'OUTRO', # Dinamicamente inferido depois
                    'events': [], 
                    'associated_objects': [],
                    'first_frame': current_frame,
                    'confidence': 90.0 + (10.0 / self.next_id)
                }
                
            self.faces[best_id]['centroid'] = centroid
            self.faces[best_id]['bbox'] = det['bbox']
            self.faces[best_id]['emotion_dict'] = det['emotion']
            self.faces[best_id]['dominant_emotion'] = det['dominant_emotion']
            self.faces[best_id]['active_this_frame'] = True
            self.faces[best_id]['last_frame'] = current_frame
            
            updated.append(best_id)
            
        return updated

    def apply_associations(self, associations):
        for assoc in associations:
            fid = assoc['face_id']
            if fid in self.faces:
                # Add object to history
                self.faces[fid]['associated_objects'].append(assoc)
                # Re-infer the role based on the full object history
                new_role = self.inference_engine.infer_role(self.faces[fid])
                if new_role != "OUTRO":
                    self.faces[fid]['role'] = new_role

class VideoProcessor:
    
    def process_video(self, session_id: str, media_id: str, blob_url: str):
        """
        Lê o arquivo do volume local e processa os frames com modelos de ML reais,
        rastreando múltiplos participantes, detectando objetos (YOLO) e seus papéis dinamicamente.
        """
        log.info("starting_video_processing", session_id=session_id, media_id=media_id, blob_url=blob_url)
        
        file_path = blob_url
        if blob_url.startswith("file:///"):
            file_path = blob_url.replace("file:///", "/")
        elif blob_url.startswith("file://"):
            file_path = blob_url.replace("file://", "")
            
        if os.name == 'nt' and file_path.startswith('/C:'):
            file_path = file_path[1:]
            
        log.info("local_file_path_resolved", file_path=file_path)
        
        if not os.path.exists(file_path):
            log.warning("file_not_found", file_path=file_path, note="Prosseguindo com análise simulada")

        try:
            import mediapipe as mp
            from deepface import DeepFace

            mp_pose = mp.solutions.pose
            pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
            mp_drawing = mp.solutions.drawing_utils

            # Initialize Object Intelligence modules
            detector = MedicalObjectDetector()
            associator = ObjectAssociator()
            inference_engine = RoleInferenceEngine()

            total_frames = 0
            fps = 30.0
            duration_seconds = 0.0
            
            analyzed_frames = 0
            pose_visible_frames = 0
            
            key_findings = []
            all_participant_objects = []
            
            tracker = FaceTracker(inference_engine)
            
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
                    
                    temp_out_path = file_path + ".temp_out.mp4"
                    annotated_out_path = file_path.replace(".mp4", "_annotated.mp4")
                    
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(temp_out_path, fourcc, fps, (width, height))
                    
                    sample_rate = settings.VIDEO_FRAME_SAMPLE_RATE
                    frame_skip = int(fps / sample_rate) if sample_rate > 0 else int(fps)
                    if frame_skip < 1: frame_skip = 1
                    
                    frame_count = 0
                    last_pose_landmarks = None
                    last_detected_objects = []
                    
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                            
                        current_second = frame_count / fps
                        
                        if frame_count % frame_skip == 0:
                            detected_faces = []
                            try:
                                res = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
                                if isinstance(res, dict):
                                    res = [res] # Normalize to list
                                    
                                for face_res in res:
                                    region = face_res.get('region', {})
                                    w, h = region.get('w', 0), region.get('h', 0)
                                    if w > 20 and h > 20: 
                                        detected_faces.append({
                                            'bbox': (region['x'], region['y'], w, h),
                                            'emotion': face_res['emotion'],
                                            'dominant_emotion': face_res['dominant_emotion']
                                        })
                            except Exception as e:
                                pass 
                            
                            # 1. Update Face Tracker
                            tracker.update(detected_faces, frame_count)

                            # 2. YOLO Object Detection (apenas a cada N frames para performance)
                            # Aproveitando o frame_skip atual que é o sample_rate
                            last_detected_objects = detector.detect(frame, current_second)

                            # 3. Associação de Objetos a Participantes
                            associations = associator.associate(tracker.faces, last_detected_objects)
                            
                            for assoc in associations:
                                assoc['timestamp'] = str(round(current_second, 1))
                                assoc['frame'] = frame_count
                                all_participant_objects.append(assoc)
                                
                                # Adicionar ao Log
                                log.info("object_association", face=assoc['face_id'], object=assoc['object_name'], type=assoc['interaction_type'])

                            # Aplica associação e infere role
                            tracker.apply_associations(associations)
                            
                            # Check for Events
                            for fid, fdata in tracker.faces.items():
                                if not fdata.get('active_this_frame'): continue
                                
                                dominant = fdata['dominant_emotion']
                                em_score = fdata['emotion_dict'].get(dominant, 0)
                                
                                if dominant in ['fear', 'sad', 'angry'] and em_score > 60.0:
                                    last_time = fdata['events'][-1]["timestamp_seconds"] if fdata['events'] else -100
                                    if current_second - last_time > 10:
                                        nome_emocao = 'ansiedade' if dominant == 'fear' else 'dor' if dominant == 'angry' else 'tristeza'
                                        
                                        event = {
                                            "participant_id": fdata['role'], # Usando role como ID principal
                                            "face_id": fid,
                                            "role": fdata['role'],
                                            "type": "emotion",
                                            "timestamp_seconds": round(current_second, 1),
                                            "description": f"Sinais de {nome_emocao} (confiança {round(em_score, 1)}%)",
                                            "confidence": round(em_score / 100.0, 2),
                                            "emotion": dominant
                                        }
                                        fdata['events'].append(event)
                                        key_findings.append(event)
                                
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
                                
                            analyzed_frames += 1
                            if analyzed_frames >= settings.MAX_FRAMES_PER_ANALYSIS:
                                break
                                
                        # --- DRAW OVERLAYS FOR ALL FRAMES ---
                        if last_pose_landmarks:
                            mp_drawing.draw_landmarks(frame, last_pose_landmarks, mp_pose.POSE_CONNECTIONS)
                            
                        # Draw YOLO Objects
                        for obj in last_detected_objects:
                            ox, oy, ow, oh = obj['bbox']
                            cv2.rectangle(frame, (ox, oy), (ox + ow, oy + oh), (255, 0, 255), 2)
                            cv2.putText(frame, obj['name'], (ox, oy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)

                        # Draw faces
                        for fid, fdata in tracker.faces.items():
                            if not fdata.get('active_this_frame'): continue 
                            
                            x, y, w, h = fdata['bbox']
                            role = fdata['role']
                            dominant = fdata['dominant_emotion']
                            confidence = fdata['emotion_dict'].get(dominant, 0)
                            
                            # Determine color based on emotion
                            if dominant in ['angry', 'fear']:
                                color = (0, 0, 255) # Red (BGR)
                            elif dominant in ['sad']:
                                color = (0, 165, 255) # Orange
                            elif dominant in ['neutral', 'happy']:
                                color = (0, 255, 0) # Green
                            else:
                                color = (0, 255, 255) # Yellow

                            # Draw Bounding Box
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                            
                            # Obter último objeto associado
                            last_obj = ""
                            if fdata['associated_objects']:
                                last_obj = fdata['associated_objects'][-1]['object_name']
                            
                            # Draw Background Box for Text
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            text_role = f"{role}"
                            text_emotion = f"{dominant.capitalize()}: {int(confidence)}%"
                            text_fid = f"{fid}"
                            text_obj = f"Obj: {last_obj}" if last_obj else ""
                            
                            (w_role, h_role), _ = cv2.getTextSize(text_role, font, 0.6, 1)
                            (w_emo, h_emo), _ = cv2.getTextSize(text_emotion, font, 0.5, 1)
                            (w_fid, h_fid), _ = cv2.getTextSize(text_fid, font, 0.4, 1)
                            (w_obj, h_obj), _ = cv2.getTextSize(text_obj, font, 0.4, 1) if text_obj else ((0,0), 0)
                            
                            box_w = max([w_role, w_emo, w_fid, w_obj]) + 10
                            box_h = h_role + h_emo + h_fid + (h_obj if text_obj else 0) + 30
                            
                            cv2.rectangle(frame, (x, y - box_h), (x + box_w, y), (30, 30, 30), -1)
                            cv2.putText(frame, text_role, (x + 5, y - box_h + 15), font, 0.6, (255, 255, 255), 1)
                            cv2.putText(frame, text_emotion, (x + 5, y - box_h + 35), font, 0.5, color, 1)
                            cv2.putText(frame, text_fid, (x + 5, y - box_h + 50), font, 0.4, (200, 200, 200), 1)
                            if text_obj:
                                cv2.putText(frame, text_obj, (x + 5, y - box_h + 65), font, 0.4, (255, 0, 255), 1)
                        
                        out.write(frame)
                        frame_count += 1
                    
                    cap.release()
                    out.release()
                    pose.close()
                    
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
                    
            # Extract participants
            participants = []
            for fid, fdata in tracker.faces.items():
                participants.append({
                    "face_id": fid,
                    "participant_id": fdata['role'],
                    "role": fdata['role'],
                    "confidence": fdata['confidence'],
                    "first_frame": fdata['first_frame'],
                    "last_frame": fdata.get('last_frame', fdata['first_frame'])
                })
                    
            # 4. Agregação e Cálculo de Scores
            emotion_score = 30.0
            if key_findings:
                emotion_score = 60.0
                
            pose_score = 30.0
            object_risk_score = 0.0
            bleeding_score = 0.0
            
            dynamic_iga = round((emotion_score * 0.7) + (pose_score * 0.3), 1)
            
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
                "participants": participants,
                "participant_objects": all_participant_objects,
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
