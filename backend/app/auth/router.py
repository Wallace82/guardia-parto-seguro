"""
GuardIA — Auth Router
Endpoints: login, refresh, logout, me, users
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreateRequest,
    UserCreatedResponse,
    UserOut,
)
from app.auth.service import AuthService
from app.database import get_db
from app.dependencies import AdminOnly, CurrentUser, GestorOrAdmin

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticar usuário e obter tokens JWT",
)
async def login(data: LoginRequest, db: DB):
    """
    Autentica com e-mail e senha.
    Retorna access token (60 min) e refresh token (7 dias).
    """
    return await AuthService(db).login(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar access token via refresh token",
)
async def refresh_token(data: RefreshTokenRequest, db: DB):
    """
    Rotaciona o refresh token: o token antigo é revogado e um novo par é emitido.
    """
    return await AuthService(db).refresh(data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revogar sessão (invalidar refresh token)",
)
async def logout(data: RefreshTokenRequest, db: DB):
    """Revoga o refresh token, encerrando a sessão no servidor."""
    await AuthService(db).logout(data.refresh_token)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Retornar dados do usuário autenticado",
)
async def get_me(current_user: CurrentUser):
    """Retorna perfil do usuário dono do token JWT."""
    return current_user


@router.post(
    "/password/change",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Trocar senha do usuário autenticado",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Troca senha verificando a senha atual antes."""
    await AuthService(db).change_password(
        current_user, data.current_password, data.new_password
    )


# ----- Gestão de usuários (admin/gestor) -----

@router.post(
    "/users",
    response_model=UserCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo usuário (admin/gestor)",
)
async def create_user(
    data: UserCreateRequest,
    current_user: GestorOrAdmin,
    db: DB,
):
    """
    Cria um novo usuário na plataforma.
    - **admin** pode criar qualquer papel
    - **gestor** pode criar apenas profissionais e auditores
    """
    user = await AuthService(db).create_user(data, current_user.role)
    return UserCreatedResponse(user=UserOut.model_validate(user))
