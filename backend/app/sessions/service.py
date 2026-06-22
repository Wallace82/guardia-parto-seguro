"""
GuardIA — Sessions Service
CRUD de sessões com controle de acesso por papel
"""
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.sessions.models import Session, SessionStatus, MediaFile, MediaStatus
from app.sessions.schemas import SessionCreateRequest, SessionUpdateRequest


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
