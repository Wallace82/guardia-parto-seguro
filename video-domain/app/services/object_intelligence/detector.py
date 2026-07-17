import cv2
import structlog
from ultralytics import YOLO
import math

log = structlog.get_logger(__name__)

class MedicalObjectDetector:
    def __init__(self, model_path='yolov8n.pt'):
        """
        Inicializa o modelo YOLOv8.
        O modelo YOLO padrão (COCO) será usado como base.
        Aplicaremos uma heurística para mapear objetos comuns para objetos médicos
        (Mocking approach para o MVP).
        """
        try:
            self.model = YOLO(model_path)
            self.ready = True
            log.info("yolo_model_loaded", model_path=model_path)
        except Exception as e:
            log.error("yolo_load_failed", error=str(e))
            self.ready = False

        # COCO class mapping for mock medical objects
        self.mock_mapping = {
            "cell phone": "Transdutor de ultrassom",
            "remote": "Transdutor de ultrassom",
            "bed": "Maca obstétrica",
            "chair": "Mesa ginecológica",
            "laptop": "Monitor multiparamétrico",
            "tv": "Monitor multiparamétrico",
            "cup": "Luvas/Instrumentos",
            "bottle": "Seringa/Medicamento",
            "book": "Prancheta",
            "tie": "Estetoscópio"
        }

    def detect(self, frame, current_time=0.0):
        """
        Retorna uma lista de objetos médicos detectados no frame.
        Cada objeto: {'name': str, 'bbox': (x, y, w, h), 'confidence': float}
        """
        if not self.ready:
            return []

        results = self.model(frame, verbose=False)
        detected_objects = []

        if len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                
                # Ignorar pessoas, focamos apenas em objetos
                class_name = self.model.names.get(cls_id, "unknown")
                if class_name == "person":
                    continue
                
                if conf < 0.25:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                w = x2 - x1
                h = y2 - y1

                # Mock mapping
                medical_name = self.mock_mapping.get(class_name)
                
                # Para MVP, se não estiver no mapping, podemos injetar uma "Barriga gestacional" 
                # ocasionalmente se detectarmos "person" na "cama", mas faremos isso em outro nível.
                if medical_name:
                    detected_objects.append({
                        "name": medical_name,
                        "raw_name": class_name,
                        "bbox": (int(x1), int(y1), int(w), int(h)),
                        "confidence": round(conf * 100, 2)
                    })

        return detected_objects
