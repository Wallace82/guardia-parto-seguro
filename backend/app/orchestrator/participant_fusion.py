import os
import json
import structlog
import openai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.sessions.analysis_models import VideoParticipant, ParticipantEvent, ParticipantObject, VideoAnalysis, AudioAnalysis

log = structlog.get_logger(__name__)

class ParticipantFusionEngine:
    """
    Motor de Fusão Transmodal (Cross-Modal Fusion)
    Cruza informações de eventos visuais (Faces/Emoções/Objetos) com transcrições
    de áudio para inferir definitivamente o papel de cada pessoa.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fuse_participants(self, session_id: int) -> dict:
        """
        Analisa os dados da sessão e retorna um dicionário mapeando
        face_id -> Role (ex: Face_001 -> PACIENTE).
        """
        log.info("starting_participant_fusion", session_id=session_id)
        
        # 1. Coletar Análises para a Sessão
        v_analysis_res = await self.db.execute(select(VideoAnalysis).where(VideoAnalysis.session_id == session_id))
        v_analysis = v_analysis_res.scalar_one_or_none()
        
        a_analysis_res = await self.db.execute(select(AudioAnalysis).where(AudioAnalysis.session_id == session_id))
        a_analysis = a_analysis_res.scalar_one_or_none()
        
        if not v_analysis or not a_analysis:
            log.warning("fusion_skipped_missing_analysis", session_id=session_id)
            return {}

        # 2. Coletar Participantes de Vídeo
        vp_result = await self.db.execute(
            select(VideoParticipant).where(VideoParticipant.video_id == v_analysis.id)
        )
        video_participants = vp_result.scalars().all()
        
        if not video_participants:
            return {}

        # 3. Coletar Eventos (Áudio e Vídeo)
        # Vamos pegar os eventos limitados para não estourar o prompt
        events_res = await self.db.execute(
            select(ParticipantEvent).order_by(ParticipantEvent.timestamp).limit(200)
        )
        events = events_res.scalars().all()
        
        # 4. Coletar Objetos
        obj_res = await self.db.execute(
            select(ParticipantObject).where(ParticipantObject.video_id == v_analysis.id)
        )
        objects = obj_res.scalars().all()

        # Construir o contexto para a OpenAI
        faces_context = []
        for vp in video_participants:
            face_objs = [o.object_name for o in objects if o.face_id == vp.face_id]
            face_evts = [f"{e.emotion} em {e.timestamp}s" for e in events if e.face_id == vp.face_id and e.event_type == 'emotion']
            faces_context.append({
                "face_id": vp.face_id,
                "current_role": vp.role,
                "objects": list(set(face_objs)),
                "emotions": face_evts[:10]  # Limita para não ficar gigante
            })
            
        audio_events = []
        for e in events:
            if e.event_type == 'speech':
                audio_events.append(f"Em {e.timestamp}s: '{e.speech}' (Falado por: {e.participant_id})")

        transcricao = a_analysis.transcricao or "Sem transcrição."
        
        # 5. Prompt para OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            log.warning("openai_fusion_skipped_no_api_key")
            return {}

        prompt = f"""
Você é um sistema de IA de inferência de papéis (Role Inference).
Seu objetivo é mapear os IDs de rostos (face_id) detectados no vídeo E os locutores do áudio (Speaker_X) aos papéis corretos na sala de parto, usando o contexto das emoções/objetos do vídeo e as transcrições do áudio em conjunto.

# Participantes Detectados (Vídeo)
{json.dumps(faces_context, indent=2, ensure_ascii=False)}

# Transcrição / Falas (Áudio)
{transcricao[:3000]}  # Limitando tamanho

# Eventos de Áudio Destacados
{chr(10).join(audio_events[:20])}

Com base nesses dados (ex: quem chora/sente dor geralmente é a PACIENTE, quem orienta ou usa bisturi é o MEDICO, acompanhante pode estar segurando celular, etc), identifique o papel correto para cada face_id E para cada locutor de áudio (Speaker_X).
Papéis permitidos: PACIENTE, MEDICO, ENFERMEIRO, ACOMPANHANTE, PEDIATRA, ANESTESISTA, OUTRO.

Retorne um JSON estritamente neste formato:
{{
  "face_roles": {{
    "Face_001": "PACIENTE",
    "Face_002": "MEDICO"
  }},
  "speaker_roles": {{
    "Speaker_1": "PACIENTE",
    "Speaker_2": "MEDICO"
  }}
}}
"""
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" },
                temperature=0.1
            )
            data_json = json.loads(response.choices[0].message.content)
            face_roles = data_json.get("face_roles", {})
            speaker_roles = data_json.get("speaker_roles", {})
            log.info("participant_fusion_success", session_id=session_id, face_roles=face_roles, speaker_roles=speaker_roles)
            
            # 6. Atualizar Banco de Dados com os Novos Papéis
            if face_roles or speaker_roles:
                for vp in video_participants:
                    if vp.face_id in face_roles:
                        new_role = face_roles[vp.face_id]
                        # Atualiza VideoParticipant
                        vp.role = new_role
                        vp.participant_id = new_role
                        
                        # Atualiza ParticipantEvent para este rosto
                        for ev in events:
                            if ev.participant_id == vp.face_id:
                                ev.participant_id = new_role
                                
                        # Atualiza ParticipantObject
                        for obj in objects:
                            if obj.face_id == vp.face_id or obj.participant_id == vp.face_id:
                                obj.participant_id = new_role
                
                # Atualizar ParticipantEvent para speakers de áudio
                if speaker_roles:
                    for ev in events:
                        if ev.participant_id in speaker_roles:
                            ev.participant_id = speaker_roles[ev.participant_id]
                
                # Opcionalmente fazer o mesmo com os alertas pendentes (já criados)
                from app.alerts.models import Alert
                alerts_res = await self.db.execute(select(Alert).where(Alert.session_id == session_id))
                alerts = alerts_res.scalars().all()
                for alert in alerts:
                    # Mapeia tanto por face_id quanto por speaker_id
                    new_role = face_roles.get(alert.participant_id) or speaker_roles.get(alert.participant_id)
                    if new_role:
                        old_participant = alert.participant_id
                        alert.participant_id = new_role
                        alert.role = new_role
                        # Altera o título se o nome genérico estiver presente
                        if alert.title and alert.title.startswith(f"⚠ {old_participant}"):
                            alert.title = alert.title.replace(old_participant, new_role)
                
                await self.db.commit()
                log.info("participant_fusion_db_updated", session_id=session_id)
                
            return face_roles
        except Exception as e:
            log.error("participant_fusion_failed", error=str(e))
            return {}
