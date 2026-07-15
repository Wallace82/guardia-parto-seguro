# BACKEND_ANALYSIS.md — GuardIA Parto Seguro

> Análise completa por engenharia reversa do backend para suportar a migração Angular.
> Autor: Agente IA | Data: 2026-07-13

---

## 1. Tecnologia

| Item | Valor |
|---|---|
| **Linguagem** | Python 3.11+ |
| **Framework Core** | FastAPI 0.110.0 |
| **Framework Frontend Atual** | Streamlit 1.35+ |
| **ORM** | SQLAlchemy 2.0 (asyncio) |
| **Driver DB** | asyncpg 0.29.0 |
| **Autenticação** | JWT (python-jose) + bcrypt (passlib) |
| **Migrations** | Alembic 1.13.1 |
| **Validação** | Pydantic v2.7.0 |
| **HTTP Client (inter-serviços)** | HTTPX 0.27.0 |
| **Logs** | structlog 24.1.0 (JSON estruturado) |
| **Banco de Dados** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Cloud** | AWS (S3, Transcribe, Comprehend, Textract, Secrets Manager, CloudWatch) |
| **Containers** | Docker + Docker Compose |
| **Testes** | pytest 8.1.1, pytest-asyncio |

---

## 2. Arquitetura

A plataforma é uma **arquitetura de microsserviços** com **8 serviços** independentes, cada um com:
- FastAPI próprio
- Banco de dados PostgreSQL isolado
- Dockerfile dedicado
- Porta HTTP exclusiva

### Orquestração de Fluxo

```
Frontend (Angular futuro)
    ↓
Core API (8000) — Gateway de entrada
    ↓ (background tasks)
    ├── Video Service (8001)
    ├── Audio Service (8002)
    ├── Document Service (8003)
    └── Risk Service (8004)
              ↓
         Report Service (8005)

AWS Domain (8007) — Hub de integração cloud
Security Service (8006) — Auditoria e LGPD
```

### Fluxo de Upload e Análise

```
1. POST /api/v1/sessions — Cria sessão (retorna session_id)
2. POST /api/v1/sessions/{id}/media — Upload de arquivo (video/audio/document)
3. (background) Orchestrator → Video/Audio/Document → Risk → Alerta
4. GET /api/v1/sessions/{id} — Consulta status e scores
5. GET /api/v1/sessions/{id}/analysis — Dados detalhados (transcrição, vídeo, risco)
6. GET /api/v1/alerts — Lista alertas gerados
```

---

## 3. Estrutura de Módulos — Core Platform (backend/)

```
backend/
├── app/
│   ├── main.py           → Ponto de entrada FastAPI, CORS, middlewares, routers
│   ├── config.py         → Settings via pydantic-settings (env vars)
│   ├── database.py       → Sessão assíncrona PostgreSQL (SQLAlchemy)
│   ├── dependencies.py   → JWT validation, RBAC (CurrentUser, AdminOnly, GestorOrAdmin)
│   ├── auth/
│   │   ├── models.py     → User, RefreshToken (SQLAlchemy)
│   │   ├── schemas.py    → LoginRequest, TokenResponse, UserOut, UserCreateRequest
│   │   ├── router.py     → /api/v1/auth/*
│   │   └── service.py    → AuthService (login, refresh, logout, create_user)
│   ├── sessions/
│   │   ├── models.py     → Session, MediaFile (SQLAlchemy)
│   │   ├── schemas.py    → SessionCreateRequest, SessionOut, MediaFileOut
│   │   ├── router.py     → /api/v1/sessions/*
│   │   └── service.py    → SessionService (CRUD + upload)
│   ├── alerts/
│   │   ├── models.py     → Alert (SQLAlchemy)
│   │   ├── schemas.py    → AlertOut, AlertListOut, AlertAcknowledgeRequest
│   │   ├── router.py     → /api/v1/alerts/*
│   │   └── service.py    → AlertService (list, acknowledge, create)
│   ├── audit/
│   │   ├── models.py     → AuditLog (SQLAlchemy)
│   │   └── service.py    → AuditService.log_action()
│   ├── orchestrator/
│   │   ├── orchestrator.py   → orchestrate_session_analysis() — orquestra background
│   │   └── domain_client.py  → DomainClient (HTTPX calls para Video/Audio/Document/Risk/Report)
│   └── middleware/
│       └── logging.py    → StructlogMiddleware (request logging)
├── migrations/           → Alembic
├── tests/
├── requirements.txt
└── Dockerfile
```

---

## 4. Domínios Existentes

| Domínio | Porta | Banco | Responsável | Tecnologias |
|---|---|---|---|---|
| Core Platform | 8000 | core_db (5432) | Dev 1 | FastAPI, SQLAlchemy, JWT |
| Video Analysis | 8001 | video_db (5433) | Dev 2 | FastAPI, OpenCV, YOLOv8, DeepFace, MediaPipe |
| Audio Analysis | 8002 | audio_db (5433) | Dev 2 | FastAPI, AWS Transcribe, AWS Comprehend |
| Document Analysis | 8003 | document_db (5433) | Dev 3 | FastAPI, AWS Textract |
| Risk Correlation | 8004 | risk_db (5433) | Dev 3 | FastAPI, cálculo ponderado IGA |
| Report Generation | 8005 | report_db (5433) | Dev 4 | FastAPI, reportlab, jinja2 |
| Security | 8006 | security_db (5433) | Dev 5 | FastAPI, LGPD, IAM |
| AWS Integration | 8007 | - | Dev 5 | FastAPI, boto3 (S3, Textract, Transcribe, CloudWatch) |
| Frontend (Streamlit) | 8501 | - | Dev 4 | Streamlit, Plotly, Pandas |

---

## 5. Entidades de Banco de Dados (Core)

### User
```
id: int (PK)
email: str (unique)
full_name: str
hashed_password: str
role: Enum(admin, gestor, profissional, auditor)
is_active: bool
created_at: datetime
updated_at: datetime
```

### RefreshToken
```
id: int (PK)
user_id: int (FK → users.id)
token_hash: str (unique, 64 chars)
expires_at: datetime
is_revoked: bool
created_at: datetime
```

### Session
```
id: int (PK)
title: str
patient_code: str  ← código anonimizado LGPD, NÃO nome real
professional_id: int (FK → users.id)
status: Enum(pending, processing, completed, error)
ira_score: float | null
ira_level: str | null  ← baixo/moderado/critico
score_video: float | null
score_audio: float | null
score_document: float | null
notes: str | null
created_at: datetime
updated_at: datetime
media_files: List[MediaFile]
```

### MediaFile
```
id: int (PK)
session_id: int (FK → sessions.id)
media_type: Enum(video, audio, document)
filename: str
blob_url: str | null  ← URL S3
file_size_bytes: int | null
content_type: str | null
status: Enum(uploaded, processing, analyzed, error)
analysis_score: float | null
error_message: str | null
uploaded_at: datetime
```

### Alert
```
id: int (PK)
session_id: int (FK → sessions.id)
alert_type: str
severity: str  ← moderate / critical
title: str
description: str
ira_score: float | null
is_acknowledged: bool
acknowledged_by: int | null (FK → users.id)
acknowledged_at: datetime | null
email_sent: bool
created_at: datetime
```

### AuditLog
```
id: int (PK)
user_id: int | null
action: str
resource: str
ip_address: str | null
timestamp: datetime
details: JSON | null
```

---

## 6. Sistema de Autenticação

### Mecanismo
- **JWT (HS256)** via python-jose
- **Access Token**: 60 minutos (configurável ACCESS_TOKEN_EXPIRE_MINUTES)
- **Refresh Token**: 7 dias (configurável REFRESH_TOKEN_EXPIRE_DAYS)
- **Refresh Token Rotation**: Token antigo é revogado ao usar /refresh
- **Logout**: Invalida refresh token no servidor (banco de dados)
- **Bearer Scheme**: Header `Authorization: Bearer <token>`

### RBAC (Roles)
| Role | Permissões |
|---|---|
| admin | Acesso total |
| gestor | Gerencia profissionais, vê todos os alertas, cria usuários |
| profissional | Cria e vê apenas suas próprias sessões |
| auditor | Leitura de relatórios e sessões |

### TokenResponse (real — implementado)
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

> DIVERGÊNCIA CRÍTICA: A API_SPEC.md mostra UserOut no login response, mas o código real retorna apenas TokenResponse sem user embutido. O frontend deve chamar GET /api/v1/auth/me separadamente após o login.

---

## 7. APIs Confirmadas no Código (Core — Porta 8000)

### Auth Module (/api/v1/auth)

| Método | Endpoint | Auth | Roles | Descrição |
|---|---|---|---|---|
| POST | /login | Não | - | Login → retorna access+refresh tokens |
| POST | /refresh | Não | - | Renova tokens via refresh token |
| POST | /logout | Não | - | Revoga refresh token |
| GET | /me | Sim | any | Retorna perfil do usuário atual |
| POST | /password/change | Sim | any | Troca senha |
| POST | /users | Sim | gestor, admin | Cria novo usuário |

### Sessions Module (/api/v1/sessions)

| Método | Endpoint | Auth | Roles | Descrição |
|---|---|---|---|---|
| POST | / | Sim | any | Cria sessão clínica |
| GET | / | Sim | any | Lista sessões (paginação: skip, limit, status) |
| GET | /{session_id} | Sim | any | Detalhe completo com media_files |
| PATCH | /{session_id} | Sim | any | Atualiza título, notas, status |
| DELETE | /{session_id} | Sim | admin, gestor | Exclui sessão |
| POST | /{session_id}/media | Sim | any | Upload multipart (file + media_type form) |
| DELETE | /media/{media_id} | Sim | any | Remove arquivo de mídia |
| GET | /{session_id}/analysis | Sim | any | Análise detalhada (transcrição, vídeo, risco) |

### Alerts Module (/api/v1/alerts)

| Método | Endpoint | Auth | Roles | Descrição |
|---|---|---|---|---|
| GET | / | Sim | any | Lista alertas (filtros: session_id, severity, unacknowledged_only) |
| GET | /{alert_id} | Sim | any | Detalhe de um alerta |
| PATCH | /{alert_id}/acknowledge | Sim | any | Reconhece alerta |
| POST | /internal | Sim | gestor, admin | Cria alerta (uso interno) |

### Health Check

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| GET | /api/v1/health | Não | Status do serviço |

---

## 8. CORS Configurado

```python
allow_origins = ["http://localhost:8501", "http://frontend:8501"]
```

> AÇÃO REQUERIDA: Para o frontend Angular rodar em http://localhost:4200, é necessário adicionar essa origem ao CORS no main.py. Isso deve ser feito de forma coordenada com Dev 1.

---

## 9. Variáveis de Ambiente Relevantes ao Frontend

```env
# Core API
SECRET_KEY=<jwt_secret>
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# IGA Thresholds (útil para UI de risco)
IRA_THRESHOLD_MODERATE=40.0
IRA_THRESHOLD_CRITICAL=70.0

# Upload limits
MAX_VIDEO_SIZE_MB=2000
MAX_AUDIO_SIZE_MB=500
MAX_DOCUMENT_SIZE_MB=50

# Serviço URLs (Angular só fala com Core na 8000)
API_BASE_URL=http://localhost:8000
```

---

## 10. APIs dos Domínios Especializados (acesso via Core)

O Angular NÃO chama diretamente os serviços de domínio. O Core API (8000) orquestra tudo. O endpoint `/api/v1/sessions/{id}/analysis` já agrega os dados de áudio, vídeo e risco.

| Serviço | URL Interna | Chamado por |
|---|---|---|
| video-service | http://video-service:8001 | Core Orchestrator (background) |
| audio-service | http://audio-service:8002 | Core Orchestrator (background) |
| document-service | http://document-service:8003 | Core Orchestrator (background) |
| risk-service | http://risk-service:8004 | Core Orchestrator (background) |
| report-service | http://report-service:8005 | Core Orchestrator (background) |
| aws-service | http://localhost:8007 | Frontend pode chamar diretamente |

---

## 11. APIs Faltantes no Backend

As seguintes APIs estão documentadas em API_SPEC.md mas NÃO têm router no código atual:

| API | Status | Impacto no Angular |
|---|---|---|
| GET /api/v1/sessions/{id}/media/{media_id} | Não implementado | Download de mídia individual |
| GET /api/v1/reports/... | Não no core-api | Relatórios via report-service (8005) |
| GET /api/v1/audit | Não exposto no core | Auditoria via security-service (8006) |
| GET /api/v1/users | Não implementado | Listagem de usuários para admin |
| PATCH /api/v1/users/{id} | Não implementado | Editar usuário |

---

## 12. Riscos de Integração

| Risco | Severidade | Mitigação |
|---|---|---|
| CORS bloqueando Angular em :4200 | ALTA | Adicionar origem ao main.py |
| TokenResponse sem user embutido | MÉDIA | Chamar GET /me após login |
| session_id é int, não UUID | MÉDIA | Usar number no TypeScript, não string |
| patient_code é string anônima, nunca CPF/nome | MÉDIA | UI nunca deve expor dados de identificação direta |
| Upload multipart usa Form(), não JSON | MÉDIA | Angular usa FormData, não JSON.stringify |
| Sessão analysis retorna null se não completed | BAIXA | Tratar estados: pending/processing/error |
| Domínios especializados não respondendo | BAIXA | Orchestrator tem fallback gracioso com mensagens padrão |
| IGA Thresholds: moderado >= 40, crítico >= 70 | INFO | Usar essas constantes na UI para codificação de cores |

---

## 13. Fluxo de Análise Detalhado (para Timeline Angular)

```
Session Status Flow:
  pending → (upload media) → processing → completed / error

MediaFile Status Flow:
  uploaded → processing → analyzed / error

IGA Risk Levels:
  0–39.9  → baixo    (verde)
  40–69.9 → moderado (amarelo)
  70–100  → critico  (vermelho)

IGA Weights (fixos no backend):
  video:    40%
  audio:    35%
  document: 25%
```

---

## 14. Frontend Atual (Streamlit) — O que Existe

O frontend Streamlit (frontend/app.py, 588 linhas) implementa:
- Login com JWT
- Dashboard com métricas de sessões e alertas
- Criação de sessão clínica
- Upload de arquivos (video/audio/document)
- Visualização de análise (transcrição, findings de vídeo, risco)
- Central de alertas com reconhecimento
- Design system: fundo escuro, cor primária violeta (#8B5CF6), Outfit font

> O Angular deve preservar a identidade visual (paleta roxa/rosa em fundo escuro) e evoluir a UX/UI.

---

*Documento gerado por engenharia reversa completa do código-fonte.*
