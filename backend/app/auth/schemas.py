"""
GuardIA — Auth Schemas (Pydantic v2)
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --------------- Request ---------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="profissional")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


# --------------- Response ---------------

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos até expirar o access token


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreatedResponse(BaseModel):
    user: UserOut
    message: str = "Usuário criado com sucesso"
