"""
GuardIA — Auth Service
Lógica de negócio para autenticação, JWT e gestão de usuários
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken, User, UserRole
from app.auth.schemas import LoginRequest, TokenResponse, UserCreateRequest
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _create_refresh_token() -> tuple[str, str]:
    """Retorna (raw_token, hash_sha256)."""
    raw = secrets.token_urlsafe(64)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


class AuthService:
    """Serviço de autenticação: login, refresh, logout e gestão de usuários."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Autentica credenciais e retorna par de tokens."""
        result = await self.db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not _verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta desativada. Contate o administrador.",
            )

        access_token = _create_access_token(user.id, user.role)
        raw_refresh, refresh_hash = _create_refresh_token()

        # Persiste refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=expires_at,
        )
        self.db.add(refresh_record)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, raw_token: str) -> TokenResponse:
        """Renova access token a partir de um refresh token válido."""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .where(RefreshToken.is_revoked.is_(False))
        )
        record = result.scalar_one_or_none()

        if not record or record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado",
            )

        # Rotaciona o refresh token (revoga o antigo, emite novo)
        record.is_revoked = True
        new_access = _create_access_token(record.user_id, record.user.role)
        new_raw, new_hash = _create_refresh_token()
        new_record = RefreshToken(
            user_id=record.user_id,
            token_hash=new_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(new_record)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_raw,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(self, raw_token: str) -> None:
        """Revoga o refresh token, invalidando a sessão."""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        record = result.scalar_one_or_none()
        if record:
            record.is_revoked = True

    async def create_user(self, data: UserCreateRequest, created_by_role: str) -> User:
        """
        Cria novo usuário. Apenas admins podem criar gestores/admins.
        """
        if data.role in ("admin", "gestor") and created_by_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas admins podem criar usuários com papel gestor ou admin",
            )
        if data.role not in [r.value for r in UserRole]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Papel inválido: {data.role}",
            )

        existing = await self.db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado",
            )

        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=_hash_password(data.password),
            role=data.role,
        )
        self.db.add(user)
        await self.db.flush()  # gera o id antes do commit
        return user

    async def list_users(self) -> list[User]:
        """Retorna todos os usuários (apenas para Admin/Gestor)."""
        result = await self.db.execute(select(User).order_by(User.created_at.desc()))
        return list(result.scalars().all())

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        """Troca senha do usuário autenticado."""
        if not _verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta",
            )
        user.hashed_password = _hash_password(new_password)
