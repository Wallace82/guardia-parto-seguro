"""
GuardIA — Sessions Router
CRUD de sessões de monitoramento
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser
from app.audit.service import AuditService
from app.sessions.schemas import (
    SessionCreateRequest,
    SessionCreatedResponse,
    SessionListOut,
    SessionOut,
    SessionUpdateRequest,
    MediaFileOut,
)
from app.sessions.service import SessionService

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/",
    response_model=SessionCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova sessão de monitoramento",
)
async def create_session(
    data: SessionCreateRequest,
    current_user: CurrentUser,
    db: DB,
):
    """
    Cria uma sessão para monitoramento de consulta/parto.
    O `patient_code` deve ser um identificador anonimizado — nunca o nome real (LGPD).
    """
    session = await SessionService(db).create(data, current_user.id)
    await AuditService.log_action(db, action="create_session", resource=f"session_{session.id}", user_id=current_user.id)
    return SessionCreatedResponse(session=SessionOut.model_validate(session))


@router.get(
    "/",
    response_model=SessionListOut,
    summary="Listar sessões (com paginação)",
)
async def list_sessions(
    current_user: CurrentUser,
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
):
    """
    Lista sessões com paginação.
    Profissionais veem apenas as próprias; gestores/admins/auditores veem todas.
    """
    total, items = await SessionService(db).list_sessions(
        user_id=current_user.id,
        user_role=current_user.role,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
    )
    return SessionListOut(total=total, items=[SessionOut.model_validate(s) for s in items])


@router.get(
    "/{session_id}",
    response_model=SessionOut,
    summary="Buscar sessão por ID",
)
async def get_session(
    session_id: int,
    current_user: CurrentUser,
    db: DB,
):
    """Retorna detalhes completos da sessão, incluindo arquivos de mídia."""
    session = await SessionService(db).get_by_id(
        session_id, current_user.id, current_user.role
    )
    await AuditService.log_action(db, action="view_session", resource=f"session_{session.id}", user_id=current_user.id)
    return SessionOut.model_validate(session)


@router.patch(
    "/{session_id}",
    response_model=SessionOut,
    summary="Atualizar dados da sessão",
)
async def update_session(
    session_id: int,
    data: SessionUpdateRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Atualiza título, notas ou status da sessão."""
    session = await SessionService(db).update(
        session_id, data, current_user.id, current_user.role
    )
    await AuditService.log_action(db, action="update_session", resource=f"session_{session.id}", user_id=current_user.id)
    return SessionOut.model_validate(session)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir sessão (admin/gestor)",
)
async def delete_session(
    session_id: int,
    current_user: CurrentUser,
    db: DB,
):
    await SessionService(db).delete(session_id, current_user.id, current_user.role)
    await AuditService.log_action(db, action="delete_session", resource=f"session_{session_id}", user_id=current_user.id)


@router.post(
    "/{session_id}/media",
    response_model=MediaFileOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Faz upload de uma mídia para a sessão",
)
async def upload_media(
    session_id: int,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: DB,
    file: UploadFile = File(...),
    media_type: str = Form(...),
):
    """
    Faz upload de um arquivo de vídeo, áudio ou documento para a sessão.
    Após o upload, inicia o processamento assíncrono em background pelo orquestrador.
    """
    if media_type not in ("video", "audio", "document"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de mídia inválido. Escolha entre: video, audio, document",
        )

    file_content = await file.read()

    media_file = await SessionService(db).add_media_file(
        session_id=session_id,
        filename=file.filename,
        content_type=file.content_type,
        media_type=media_type,
        file_content=file_content,
        user_id=current_user.id,
        user_role=current_user.role,
    )

    # Dispara o orquestrador em background
    from app.orchestrator.orchestrator import orchestrate_session_analysis
    background_tasks.add_task(orchestrate_session_analysis, session_id)

    return media_file
