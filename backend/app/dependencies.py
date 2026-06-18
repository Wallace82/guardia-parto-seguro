"""
GuardIA Parto Seguro — FastAPI Dependencies
JWT validation, current user, RBAC role enforcement
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

# Extrai Bearer token do header Authorization
bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Valida JWT e retorna o usuário autenticado.
    Levanta 401 se token inválido ou expirado.
    """
    # Import aqui para evitar circular import
    from app.auth.models import User
    from sqlalchemy import select

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_role(*roles: str):
    """
    Factory de dependency para RBAC.
    Uso: Depends(require_role('admin', 'gestor'))
    """
    async def _check_role(
        current_user=Depends(get_current_user),
    ):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Papel exigido: {', '.join(roles)}",
            )
        return current_user
    return _check_role


# Aliases prontos para uso nos routers
CurrentUser = Annotated[object, Depends(get_current_user)]
AdminOnly = Annotated[object, Depends(require_role("admin"))]
GestorOrAdmin = Annotated[object, Depends(require_role("admin", "gestor"))]
AnyAuthenticated = Annotated[object, Depends(get_current_user)]
