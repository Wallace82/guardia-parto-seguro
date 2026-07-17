import math

class ObjectAssociator:
    def __init__(self):
        pass

    def _get_center(self, bbox):
        x, y, w, h = bbox
        return (x + w/2, y + h/2)

    def _get_distance(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def _check_overlap(self, bbox1, bbox2):
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2

        if x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2:
            return True
        return False

    def associate(self, faces, detected_objects):
        """
        Relaciona rostos aos objetos baseados em distância e overlap.
        faces: dict de fid -> {bbox, ...}
        detected_objects: lista de objetos detectados [{'name', 'bbox', ...}]
        
        Retorna uma lista de associações:
        [{'face_id': 'Face_001', 'object_name': 'Transdutor', 'interaction_type': 'manipulando'}, ...]
        """
        associations = []

        for fid, fdata in faces.items():
            if not fdata.get('active_this_frame'): continue
            
            f_bbox = fdata['bbox']
            f_center = self._get_center(f_bbox)
            # Expandir o corpo da face (estimativa simples: corpo está abaixo do rosto)
            fx, fy, fw, fh = f_bbox
            body_bbox = (fx - fw, fy, fw * 3, fh * 4)

            for obj in detected_objects:
                o_bbox = obj['bbox']
                o_center = self._get_center(o_bbox)

                # Verificar se objeto se sobrepõe ao corpo "estimado" (Manipulação)
                if self._check_overlap(body_bbox, o_bbox):
                    associations.append({
                        'face_id': fid,
                        'object_name': obj['name'],
                        'interaction_type': 'manipulando',
                        'confidence': obj['confidence']
                    })
                else:
                    # Verificar se objeto está próximo (Próximo)
                    # Limiar de proximidade (ex: 3 vezes a altura do rosto)
                    dist = self._get_distance(f_center, o_center)
                    if dist < (fh * 3):
                        associations.append({
                            'face_id': fid,
                            'object_name': obj['name'],
                            'interaction_type': 'proximo',
                            'confidence': obj['confidence']
                        })

        return associations
