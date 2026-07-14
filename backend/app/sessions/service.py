"""
GuardIA — Sessions Service
CRUD de sessões com controle de acesso por papel
"""
from fastapi import HTTPException, status
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.sessions.models import Session, SessionStatus, MediaFile, MediaStatus
from app.sessions.schemas import SessionCreateRequest, SessionUpdateRequest

import structlog
from app.database import AsyncSessionLocal
from app.sessions.analysis_models import DocumentAnalysis
from app.orchestrator.domain_client import DomainClient

log = structlog.get_logger(__name__)

async def process_notes_background(session_id: int, notes: str):
    """Executa a análise textual das notas em background e registra no BD."""
    try:
        from app.sessions.models import Session
        client = DomainClient()
        analysis_data = await client.analyze_notes(session_id, notes)
        analysis_text = analysis_data.get("analysis", "")
        clinical_risk_score = analysis_data.get("clinical_risk_score", 0.0)
        
        async with AsyncSessionLocal() as db:
            # Apagar análise anterior se houver
            await db.execute(
                delete(DocumentAnalysis).where(
                    DocumentAnalysis.session_id == session_id,
                    DocumentAnalysis.tipo_documento == "anotacoes"
                )
            )
            
            structured = analysis_data.get("structured_analysis", {})
            
            # Derivando confidence score a partir da qualidade da informacao
            qualidade = structured.get("qualidade_informacao", {}).get("nivel", "")
            conf_score = 95.0 if qualidade == "ALTA" else (70.0 if qualidade == "MEDIA" else 40.0)
            
            # Simulando os scores de risco especificos com base na intensidade geral
            psycho_risk = 80.0 if structured.get("aspectos_emocionais", {}).get("nivel") in ["ALTA", "ELEVADO"] else 20.0
            
            d_analysis = DocumentAnalysis(
                session_id=session_id,
                arquivo_documento="Anotações Clínicas (Multimodal)",
                tipo_documento="anotacoes",
                texto_extraido=notes,
                clinical_risk_score=clinical_risk_score,
                psychological_risk_score=psycho_risk,
                pregnancy_risk_score=clinical_risk_score,
                confidence_score=conf_score,
                entidades_detectadas=structured,
                fatores_identificados={
                    "analise_textual": analysis_text,
                    "estruturado": structured
                }
            )
            db.add(d_analysis)
            
            # Buscar sessão para atualizar scores
            session = await db.get(Session, session_id)
            if session:
                session.score_notes = clinical_risk_score
                
                # Para calcular o document_score unificado, pegar a nota do prontuario pdf se existir
                doc_score = session.score_document
                final_doc_score = max(doc_score or 0.0, clinical_risk_score)
                
                # Recalcular IRA
                risk_res = await client.correlate_risk(
                    session_id=session_id,
                    patient_code=session.patient_code,
                    video_score=session.score_video,
                    audio_score=session.score_audio,
                    document_score=final_doc_score
                )
                session.ira_score = risk_res.get("ira_score", 0.0)
                session.ira_level = risk_res.get("risk_level", "baixo")
            
            await db.commit()
            return analysis_text
    except Exception as e:
        log.error("background_notes_analysis_failed", session_id=session_id, error=str(e))



class SessionService:
    """Gerencia o ciclo de vida das sessões de monitoramento."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: SessionCreateRequest, professional_id: int) -> Session:
        """Cria uma nova sessão de monitoramento."""
        session = Session(
            title=data.title,
            patient_code=data.patient_code,
            professional_id=professional_id,
            notes=data.notes,
            status=SessionStatus.pending,
            media_files=[]
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_id(self, session_id: int, user_id: int, user_role: str) -> Session:
        """
        Busca sessão por ID com controle de acesso:
        - profissional: apenas as próprias sessões
        - gestor/admin/auditor: todas
        """
        result = await self.db.execute(
            select(Session)
            .options(selectinload(Session.media_files))
            .where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada",
            )
        if user_role == "profissional" and session.professional_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a esta sessão",
            )
        return session

    async def list_sessions(
        self,
        user_id: int,
        user_role: str,
        skip: int = 0,
        limit: int = 20,
        status_filter: str | None = None,
    ) -> tuple[int, list[Session]]:
        """Lista sessões com paginação e filtro opcional por status."""
        query = select(Session).options(selectinload(Session.media_files))

        # Profissionais veem apenas suas sessões
        if user_role == "profissional":
            query = query.where(Session.professional_id == user_id)

        if status_filter:
            query = query.where(Session.status == status_filter)

        query = query.order_by(Session.created_at.desc())

        # Total sem paginação
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        result = await self.db.execute(query.offset(skip).limit(limit))
        items = list(result.scalars().all())

        return total, items

    async def update(
        self,
        session_id: int,
        data: SessionUpdateRequest,
        user_id: int,
        user_role: str,
    ) -> Session:
        """Atualiza dados editáveis da sessão."""
        session = await self.get_by_id(session_id, user_id, user_role)

        # Profissionais não podem alterar status manualmente
        if data.status and user_role == "profissional":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profissionais não podem alterar o status da sessão",
            )

        if data.title is not None:
            session.title = data.title
        if data.notes is not None:
            session.notes = data.notes
            session.score_notes = None # Reseta o score para forçar o recálculo e o polling do frontend
        if data.status is not None:
            session.status = data.status

        return session

    async def delete(self, session_id: int, user_id: int, user_role: str) -> None:
        """Exclui sessão (apenas admin/gestor)."""
        if user_role not in ("admin", "gestor"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas admins e gestores podem excluir sessões",
            )
        session = await self.get_by_id(session_id, user_id, user_role)
        await self.db.delete(session)

    async def add_media_file(
        self,
        session_id: int,
        filename: str,
        content_type: str,
        media_type: str,
        file_content: bytes,
        user_id: int,
        user_role: str,
    ) -> MediaFile:
        """Adiciona um arquivo de mídia à sessão."""
        session = await self.get_by_id(session_id, user_id, user_role)
        
        blob_url = None
        file_size = len(file_content)
        
        if not blob_url:
            # Salvar localmente
            import os
            # Usa o volume compartilhado no Docker, ou um valor local default
            uploads_dir = os.environ.get("SHARED_MEDIA_DIR", "/shared_media")
            os.makedirs(uploads_dir, exist_ok=True)
            file_path = os.path.join(uploads_dir, f"{session_id}_{media_type}_{filename}")
            with open(file_path, "wb") as f:
                f.write(file_content)
            # URL local mockada
            blob_url = f"file:///{file_path.replace(os.sep, '/')}"

        media_file = MediaFile(
            session_id=session.id,
            media_type=media_type,
            filename=filename,
            blob_url=blob_url,
            file_size_bytes=file_size,
            content_type=content_type,
            status=MediaStatus.uploaded,
        )
        self.db.add(media_file)
        await self.db.flush()
        
        # Atualiza status da sessão para processing
        session.status = SessionStatus.processing
        
        return media_file

    async def delete_media_file(
        self,
        media_id: int,
        user_id: int,
        user_role: str,
    ) -> None:
        """Exclui um arquivo de mídia pelo ID."""
        query = select(MediaFile).where(MediaFile.id == media_id)
        result = await self.db.execute(query)
        media_file = result.scalar_one_or_none()
        
        if not media_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo de mídia não encontrado",
            )
            
        # Buscar sessão associada para verificar permissões de acesso
        session = await self.get_by_id(media_file.session_id, user_id, user_role)
        
        # Deletar arquivo físico se existir
        import os
        uploads_dir = os.environ.get("SHARED_MEDIA_DIR", "/shared_media")
        file_path = os.path.join(uploads_dir, f"{session.id}_{media_file.media_type}_{media_file.filename}")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
                
        # Remover registros de análise associados à mídia
        if media_file.media_type == "video":
            from app.sessions.analysis_models import VideoAnalysis
            await self.db.execute(delete(VideoAnalysis).where(VideoAnalysis.session_id == session.id, VideoAnalysis.arquivo_video == media_file.filename))
        elif media_file.media_type == "audio":
            from app.sessions.analysis_models import AudioAnalysis
            await self.db.execute(delete(AudioAnalysis).where(AudioAnalysis.session_id == session.id, AudioAnalysis.arquivo_audio == media_file.filename))
        elif media_file.media_type == "document":
            from app.sessions.analysis_models import DocumentAnalysis
            await self.db.execute(delete(DocumentAnalysis).where(DocumentAnalysis.session_id == session.id, DocumentAnalysis.arquivo_documento == media_file.filename))

        # Remover do banco
        await self.db.delete(media_file)
        await self.db.commit()

        # Recalcular os índices e o IRA da sessão
        await self._recalculate_session_risk(session.id)

    async def _recalculate_session_risk(self, session_id: int):
        from app.sessions.analysis_models import VideoAnalysis, AudioAnalysis, DocumentAnalysis
        from app.risk_engine.fusion_service import RiskFusionEngine
        
        session = await self.db.get(Session, session_id)
        if not session:
            return

        result = await self.db.execute(select(VideoAnalysis).where(VideoAnalysis.session_id == session_id))
        video_analyses = result.scalars().all()
        
        result = await self.db.execute(select(AudioAnalysis).where(AudioAnalysis.session_id == session_id))
        audio_analyses = result.scalars().all()
        
        result = await self.db.execute(select(DocumentAnalysis).where(DocumentAnalysis.session_id == session_id))
        doc_analyses = result.scalars().all()

        fusion_result = RiskFusionEngine.calculate_session_risk(
            list(video_analyses), list(audio_analyses), list(doc_analyses), session.notes
        )
        
        session.ira_score = fusion_result["globalScore"]
        risk_level = fusion_result["riskLevel"].lower()
        if risk_level == "medium":
            session.ira_level = "moderado"
        elif risk_level == "high":
            session.ira_level = "critico"
        elif risk_level == "low":
            session.ira_level = "baixo"
        else:
            session.ira_level = risk_level

        session.score_video = fusion_result["sources"].get("video")
        session.score_audio = fusion_result["sources"].get("audio")
        session.score_document = fusion_result["sources"].get("document")
        session.score_notes = fusion_result["sources"].get("notes")

        await self.db.commit()

    async def get_dashboard_metrics(self) -> dict:
        """Agrega as métricas para o Dashboard Home (visão global)."""
        from app.alerts.models import Alert
        
        # Total de sessões
        result_sessions = await self.db.execute(select(func.count()).select_from(Session))
        total_sessions = result_sessions.scalar() or 0
        
        # Alertas críticos não resolvidos
        result_alerts = await self.db.execute(
            select(func.count()).select_from(Alert)
            .where(Alert.severity == "critical")
            .where(Alert.is_acknowledged == False)
        )
        critical_alerts = result_alerts.scalar() or 0
        
        # Média IRA
        result_ira = await self.db.execute(
            select(func.avg(Session.ira_score)).where(Session.ira_score.isnot(None))
        )
        avg_ira = result_ira.scalar() or 0.0
        
        # Distribuição Mensal Mockada (para simplificar a compatibilidade cross-DB)
        # Numa base real faríamos um group by truncando o created_at
        monthly_distribution = [
            {"label": "Jan", "value": max(0, total_sessions - 150)},
            {"label": "Fev", "value": max(0, total_sessions - 120)},
            {"label": "Mar", "value": max(0, total_sessions - 80)},
            {"label": "Abr", "value": max(0, total_sessions - 40)},
            {"label": "Mai", "value": max(0, total_sessions - 10)},
            {"label": "Jun", "value": total_sessions},
        ]
        
        return {
            "total_sessions": total_sessions,
            "critical_alerts": critical_alerts,
            "average_ira": float(avg_ira),
            "monthly_distribution": monthly_distribution
        }
