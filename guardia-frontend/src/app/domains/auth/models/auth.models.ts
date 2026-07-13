// =====================================================================
// Auth Domain — TypeScript Models
// Mapeados 1:1 com os schemas Pydantic do backend/app/auth/schemas.py
// =====================================================================

export type UserRole = 'admin' | 'gestor' | 'profissional' | 'auditor';

/** backend: LoginRequest */
export interface LoginCredentials {
  email: string;
  password: string;
}

/** backend: TokenResponse — NÃO inclui user (chamar GET /me após login) */
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number; // segundos — 3600 = 60min
}

/** backend: RefreshTokenRequest */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/** backend: UserOut */
export interface UserProfile {
  id: number;           // int, não UUID
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;   // ISO 8601
}

/** backend: UserCreateRequest */
export interface CreateUserRequest {
  email: string;
  full_name: string;
  password: string;     // mín. 8 chars
  role?: UserRole;      // default: 'profissional'
}

/** backend: UserCreatedResponse */
export interface CreateUserResponse {
  user: UserProfile;
  message: string;
}

/** backend: ChangePasswordRequest */
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

/** Logout request */
export interface LogoutRequest {
  refresh_token: string;
}
