# frontend-models.md — GuardIA Parto Seguro

> Mapeamento: Backend DTO → Interface TypeScript Angular
> Baseado em: backend/app/*/schemas.py e models.py

---

## Convenções

- Backend usa `int` para IDs → Angular usa `number`
- Backend usa `float | null` → Angular usa `number | null`
- Backend usa `str | None` → Angular usa `string | null`
- Backend usa `datetime` → Angular usa `string` (ISO 8601)
- Backend usa `bool` → Angular usa `boolean`
- Backend usa `List[T]` → Angular usa `T[]`
- Enums são strings literais

---

## 1. Auth Domain

### Backend: `LoginRequest` → Angular: `LoginCredentials`

```typescript
// src/app/domains/auth/models/login-credentials.model.ts
export interface LoginCredentials {
  email: string;
  password: string;
}
```

### Backend: `TokenResponse` → Angular: `AuthTokens`

```typescript
// src/app/domains/auth/models/auth-tokens.model.ts
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number; // segundos
}
```

### Backend: `UserOut` → Angular: `UserProfile`

```typescript
// src/app/domains/auth/models/user-profile.model.ts
export type UserRole = 'admin' | 'gestor' | 'profissional' | 'auditor';

export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string; // ISO 8601
}
```

### Backend: `UserCreateRequest` → Angular: `CreateUserRequest`

```typescript
// src/app/domains/auth/models/create-user-request.model.ts
export interface CreateUserRequest {
  email: string;
  full_name: string;
  password: string;
  role?: UserRole; // default: 'profissional'
}
```

### Backend: `UserCreatedResponse` → Angular: `CreateUserResponse`

```typescript
export interface CreateUserResponse {
  user: UserProfile;
  message: string;
}
```

### Backend: `RefreshTokenRequest` → Angular: `RefreshTokenRequest`

```typescript
export interface RefreshTokenRequest {
  refresh_token: string;
}
```

### Backend: `ChangePasswordRequest` → Angular: `ChangePasswordRequest`

```typescript
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}
```

---

## 2. Sessions Domain

### Backend: `SessionCreateRequest` → Angular: `CreateSessionRequest`

```typescript
// src/app/domains/sessoes/models/create-session-request.model.ts
export interface CreateSessionRequest {
  title: string;        // mín 3, máx 255 chars
  patient_code: string; // mín 3, máx 64 chars — LGPD: código anonimizado
  notes?: string | null; // máx 2000 chars
}
```

### Backend: `SessionUpdateRequest` → Angular: `UpdateSessionRequest`

```typescript
export interface UpdateSessionRequest {
  title?: string | null;
  notes?: string | null;
  status?: SessionStatus | null;
}
```

### Backend: `MediaFileOut` → Angular: `MediaFile`

```typescript
// src/app/domains/sessoes/models/media-file.model.ts
export type MediaType = 'video' | 'audio' | 'document';
export type MediaStatus = 'uploaded' | 'processing' | 'analyzed' | 'error';

export interface MediaFile {
  id: number;
  media_type: MediaType;
  filename: string;
  blob_url: string | null;
  file_size_bytes: number | null;
  status: MediaStatus;
  analysis_score: number | null;
  uploaded_at: string; // ISO 8601
}
```

### Backend: `SessionOut` → Angular: `ClinicalSession`

```typescript
// src/app/domains/sessoes/models/clinical-session.model.ts
export type SessionStatus = 'pending' | 'processing' | 'completed' | 'error';
export type IraLevel = 'baixo' | 'moderado' | 'critico';

export interface ClinicalSession {
  id: number;
  title: string;
  patient_code: string;
  professional_id: number;
  status: SessionStatus;
  ira_score: number | null;
  ira_level: IraLevel | null;
  score_video: number | null;
  score_audio: number | null;
  score_document: number | null;
  notes: string | null;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  media_files: MediaFile[];
}
```

### Backend: `SessionListOut` → Angular: `SessionListResponse`

```typescript
export interface SessionListResponse {
  total: number;
  items: ClinicalSession[];
}
```

### Backend: `SessionCreatedResponse` → Angular: `CreateSessionResponse`

```typescript
export interface CreateSessionResponse {
  session: ClinicalSession;
  message: string;
}
```

---

## 3. Analysis Domain (endpoint agregado)

### Resposta de `GET /sessions/{id}/analysis` → Angular: `SessionAnalysis`

```typescript
// src/app/domains/analise-ia/models/session-analysis.model.ts

export interface TranscriptionSegment {
  speaker: string;
  role: 'profissional' | 'paciente' | string;
  start: number; // segundos
  end: number;   // segundos
  text: string;
  sentiment: 'positive' | 'negative' | 'neutral' | 'mixed';
  sentiment_confidence: number; // 0.0 a 1.0
}

export interface Transcription {
  full_text: string;
  segments: TranscriptionSegment[];
}

export interface VideoFinding {
  type: string; // 'emotion', 'pose', 'bleeding', 'object'
  timestamp_seconds: number;
  description: string;
  confidence: number; // 0.0 a 1.0
}

export interface RiskComponent {
  text: string;
  key_indicators: string[];
  recommendation: string;
}

export interface RiskDetails {
  video: RiskComponent;
  audio: RiskComponent;
  document: RiskComponent;
}

export interface SessionAnalysis {
  session_id: number;
  status: SessionStatus;
  transcription: Transcription | null;
  video_findings: VideoFinding[];
  video_analyses: Record<string, unknown>;
  risk_details: RiskDetails | null;
}
```

---

## 4. Alerts Domain

### Backend: `AlertOut` → Angular: `Alert`

```typescript
// src/app/domains/alertas/models/alert.model.ts
export type AlertSeverity = 'moderate' | 'critical';

export interface Alert {
  id: number;
  session_id: number;
  alert_type: string;
  severity: AlertSeverity;
  title: string;
  description: string;
  ira_score: number | null;
  is_acknowledged: boolean;
  acknowledged_by: number | null;
  acknowledged_at: string | null; // ISO 8601
  email_sent: boolean;
  created_at: string; // ISO 8601
}
```

### Backend: `AlertListOut` → Angular: `AlertListResponse`

```typescript
export interface AlertListResponse {
  total: number;
  items: Alert[];
}
```

### Angular: `AlertsFilter` (para query params)

```typescript
export interface AlertsFilter {
  session_id?: number;
  severity?: AlertSeverity;
  unacknowledged_only?: boolean;
  skip?: number;
  limit?: number;
}
```

---

## 5. Upload Domain

### Angular: `MediaUploadRequest` (para FormData)

```typescript
// src/app/domains/sessoes/models/media-upload.model.ts
export interface MediaUploadRequest {
  file: File;
  media_type: MediaType;
}
```

---

## 6. IGA / Risk Constants

```typescript
// src/app/shared/constants/ira.constants.ts
export const IRA_THRESHOLDS = {
  MODERATE: 40.0,
  CRITICAL: 70.0,
} as const;

export const IRA_WEIGHTS = {
  VIDEO: 0.40,
  AUDIO: 0.35,
  DOCUMENT: 0.25,
} as const;

export function getIraLevel(score: number): IraLevel {
  if (score >= IRA_THRESHOLDS.CRITICAL) return 'critico';
  if (score >= IRA_THRESHOLDS.MODERATE) return 'moderado';
  return 'baixo';
}

export function getIraColor(level: IraLevel): string {
  const colors: Record<IraLevel, string> = {
    baixo: '#10B981',    // verde esmeralda
    moderado: '#F59E0B', // âmbar
    critico: '#EF4444',  // vermelho
  };
  return colors[level];
}
```

---

## 7. Paginação Genérica

```typescript
// src/app/shared/models/paginated-response.model.ts
export interface PaginatedResponse<T> {
  total: number;
  items: T[];
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}
```

---

## 8. Error Response

```typescript
// src/app/shared/models/api-error.model.ts
export interface ApiError {
  detail: string | ValidationError[];
}

export interface ValidationError {
  type: string;
  loc: (string | number)[];
  msg: string;
  input: unknown;
}
```

---

## 9. Health Check

```typescript
// src/app/shared/models/health.model.ts
export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  version: string;
  environment: string;
}
```

---

## Mapa Completo Backend ↔ Angular

| Backend Schema | Angular Interface | Arquivo |
|---|---|---|
| `LoginRequest` | `LoginCredentials` | `domains/auth/models/login-credentials.model.ts` |
| `TokenResponse` | `AuthTokens` | `domains/auth/models/auth-tokens.model.ts` |
| `UserOut` | `UserProfile` | `domains/auth/models/user-profile.model.ts` |
| `UserCreateRequest` | `CreateUserRequest` | `domains/auth/models/create-user-request.model.ts` |
| `RefreshTokenRequest` | `RefreshTokenRequest` | `domains/auth/models/` |
| `ChangePasswordRequest` | `ChangePasswordRequest` | `domains/auth/models/` |
| `SessionCreateRequest` | `CreateSessionRequest` | `domains/sessoes/models/create-session-request.model.ts` |
| `SessionUpdateRequest` | `UpdateSessionRequest` | `domains/sessoes/models/` |
| `SessionOut` | `ClinicalSession` | `domains/sessoes/models/clinical-session.model.ts` |
| `SessionListOut` | `SessionListResponse` | `domains/sessoes/models/` |
| `MediaFileOut` | `MediaFile` | `domains/sessoes/models/media-file.model.ts` |
| `AlertOut` | `Alert` | `domains/alertas/models/alert.model.ts` |
| `AlertListOut` | `AlertListResponse` | `domains/alertas/models/` |
| `SessionAnalysis` (agregada) | `SessionAnalysis` | `domains/analise-ia/models/session-analysis.model.ts` |

---

*Documento baseado no código real: backend/app/auth/schemas.py, sessions/schemas.py, alerts/schemas.py*
