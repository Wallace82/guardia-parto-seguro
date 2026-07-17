class RoleInferenceEngine:
    def __init__(self):
        # Base scores
        self.patient_objects = ["Maca obstétrica", "Barriga gestacional", "Avental hospitalar"]
        self.medical_objects = ["Transdutor de ultrassom", "Luvas/Instrumentos", "Monitor multiparamétrico", "Seringa/Medicamento", "Prancheta", "Estetoscópio"]
        self.companion_objects = [] # Companions usually don't have medical equipment
        
    def infer_role(self, face_history):
        """
        Recebe o histórico de um rosto e infere o papel.
        face_history: {'events': [...], 'associated_objects': [ {'object_name': 'Transdutor', 'interaction_type': 'manipulando'}, ... ]}
        """
        score_patient = 0
        score_medical = 0
        score_companion = 0
        
        objects = face_history.get('associated_objects', [])
        
        if not objects:
            # Sem objetos, e se não é paciente nem médico, provável acompanhante ou outro.
            # Um palpite inicial baseado em ID
            return "OUTRO"

        for obj_ev in objects:
            obj_name = obj_ev.get('object_name')
            interaction = obj_ev.get('interaction_type')
            
            # Médico
            if obj_name in self.medical_objects:
                if interaction == 'manipulando':
                    score_medical += 100
                else:
                    score_medical += 50
                    
            # Paciente
            if obj_name in self.patient_objects:
                if interaction == 'manipulando':
                    score_patient += 30 # Paciente raramente manipula maca, mas "está" nela (sobreposição)
                else:
                    score_patient += 80 # Próximo a maca
                    
        # Determinar o vencedor
        if score_medical == 0 and score_patient == 0:
            # Se a pessoa está sempre presente mas não manipula equipamento médico, e não está na maca,
            # Alta chance de ser acompanhante.
            score_companion = 50

        max_score = max(score_patient, score_medical, score_companion)
        
        if max_score == 0:
            return "OUTRO"
            
        if max_score == score_medical:
            return "EQUIPE_MEDICA_1" # Ou identificar _1, _2 dependendo de contagem
        elif max_score == score_patient:
            return "PACIENTE"
        else:
            return "ACOMPANHANTE"
