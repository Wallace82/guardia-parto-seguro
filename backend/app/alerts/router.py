"""
GuardIA — Alerts Router
Endpoints para listagem e reconhecimento de alertas
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.schemas import AlertCreateRequest, AlertListOut, AlertOut
from app.alerts.service import AlertService
from app.database import get_db
from app.dependencies import CurrentUser, GestorOrAdmin

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=AlertListOut,
    summary="Listar alertas com filtros",
)
async def list_alerts(
    current_user: CurrentUser,
    db: DB,
    session_id: int | None = Query(default=None),
    severity: str | None = Query(default=None),
    unacknowledged_only: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """
    Lista alertas com filtros opcionais.
    - `session_id`: filtra por sessão específica
    - `severity`: `moderate` ou `critical`
    - `unacknowledged_only`: apenas alertas não reconhecidos
    """
    total, items = await AlertService(db).list_alerts(
        user_role=current_user.role,
        session_id=session_id,
        severity=severity,
        unacknowledged_only=unacknowledged_only,
        skip=skip,
        limit=limit,
    )
    return AlertListOut(total=total, items=[AlertOut.model_validate(a) for a in items])


@router.get(
    "/{alert_id}",
    response_model=AlertOut,
    summary="Buscar alerta por ID",
)
async def get_alert(alert_id: int, current_user: CurrentUser, db: DB):
    """Retorna detalhes de um alerta específico."""
    _, items = await AlertService(db).list_alerts(user_role=current_user.role)
    alert = next((a for a in items if a.id == alert_id), None)
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta não encontrado")
    return AlertOut.model_validate(alert)


@router.patch(
    "/{alert_id}/acknowledge",
    response_model=AlertOut,
    summary="Reconhecer alerta",
)
async def acknowledge_alert(
    alert_id: int,
    current_user: CurrentUser,
    db: DB,
):
    """
    Marca o alerta como reconhecido pelo usuário autenticado.
    Profissionais, gestores e admins podem reconhecer alertas.
    """
    alert = await AlertService(db).acknowledge(alert_id, current_user.id)
    return AlertOut.model_validate(alert)


@router.patch(
    "/{alert_id}/dismiss",
    response_model=AlertOut,
    summary="Ignorar alerta",
)
async def dismiss_alert(
    alert_id: int,
    current_user: CurrentUser,
    db: DB,
):
    """
    Marca o alerta como ignorado (ex: falso positivo).
    """
    alert = await AlertService(db).dismiss(alert_id, current_user.id)
    return AlertOut.model_validate(alert)


@router.post(
    "/internal",
    response_model=AlertOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar alerta (uso interno — risk-service)",
    include_in_schema=False,  # Oculto do Swagger público
)
async def create_alert_internal(
    data: AlertCreateRequest,
    current_user: GestorOrAdmin,
    db: DB,
):
    """
    Endpoint interno para o risk-service criar alertas.
    Requer papel gestor ou admin.
    """
    alert = await AlertService(db).create_alert(data)
    return AlertOut.model_validate(alert)
