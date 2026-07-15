# API_CONTRACTS.md — GuardIA Parto Seguro

> Contratos de API para o Frontend Angular — verificados contra código-fonte real.
> Base URL: `http://localhost:8000/api/v1`
> Auth: `Authorization: Bearer <access_token>`

---

## Convenções

- **IDs**: `number` (int, não UUID)
- **Datas**: ISO 8601 string (`datetime`)
- **Paginação**: `?skip=0&limit=20`
- **Upload**: `multipart/form-data` (não JSON)
- **Erros**: `{ "detail": "mensagem" }`

---

## 1. Autenticação

### POST /api/v1/auth/login

**Descrição**: Autentica usuário e retorna tokens JWT.

**Auth**: Não requerida

**Request Body**:
```json
{
  "email": "medico@hospital.com",
  "password": "senha_segura"
}
```

**Campos obrigatórios**: `email`, `password` (mín. 8 chars)

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Response 401**: `{ "detail": "Credenciais inválidas" }`
**Response 422**: Falha de validação Pydantic

**Regras de negócio**:
- Após o login, chamar `GET /me` para obter dados do usuário
- Armazenar `access_token` e `refresh_token` separadamente
- `expires_in` está em **segundos** (3600 = 60 min)

---

### POST /api/v1/auth/refresh

**Descrição**: Renova tokens (rotation — antigo é invalidado).

**Auth**: Não requerida

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200**: Mesmo formato de `TokenResponse`

**Regras de negócio**:
- O refresh token antigo é **invalidado** após uso
- Salvar o novo par de tokens retornado
- Chamar automaticamente quando access_token expirar (401)

---

### POST /api/v1/auth/logout

**Descrição**: Invalida o refresh token no servidor.

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 204**: No content

---

### GET /api/v1/auth/me

**Descrição**: Retorna dados do usuário autenticado.

**Auth**: Requerida (Bearer)

**Response 200**:
```json
{
  "id": 1,
  "email": "medico@hospital.com",
  "full_name": "Dr. João Silva",
  "role": "profissional",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Roles possíveis**: `admin`, `gestor`, `profissional`, `auditor`

---

### POST /api/v1/auth/password/change

**Auth**: Requerida

**Request Body**:
```json
{
  "current_password": "senha_atual",
  "new_password": "nova_senha_segura"
}
```

**Response 204**: No content
**Response 400**: Senha atual incorreta

---

### POST /api/v1/auth/users

**Descrição**: Cria novo usuário (admin/gestor apenas).

**Auth**: Requerida | **Roles**: `admin`, `gestor`

**Request Body**:
```json
{
  "email": "novo@hospital.com",
  "full_name": "Dra. Maria Santos",
  "password": "senha_segura123",
  "role": "profissional"
}
```

**Campos opcionais**: `role` (default: `"profissional"`)

**Response 201**:
```json
{
  "user": { /* UserOut */ },
  "message": "Usuário criado com sucesso"
}
```

**Erros**:
- `409`: Email já cadastrado
- `403`: Gestor tentando criar admin

---

## 2. Sessões Clínicas

### POST /api/v1/sessions

**Descrição**: Cria nova sessão de monitoramento.

**Auth**: Requerida

**Request Body**:
```json
{
  "title": "Consulta Pré-natal - Semana 36",
  "patient_code": "PAC-2024-001",
  "notes": "Paciente com histórico de hipertensão"
}
```

**Campos obrigatórios**: `title` (mín. 3, máx. 255 chars), `patient_code` (mín. 3, máx. 64 chars)
**Campos opcionais**: `notes` (máx. 2000 chars)

**LGPD**: `patient_code` deve ser código anonimizado — NUNCA CPF, nome completo ou dados pessoais.

**Response 201**:
```json
{
  "session": {
    "id": 42,
    "title": "Consulta Pré-natal - Semana 36",
    "patient_code": "PAC-2024-001",
    "professional_id": 1,
    "status": "pending",
    "ira_score": null,
    "ira_level": null,
    "score_video": null,
    "score_audio": null,
    "score_document": null,
    "notes": "Paciente com histórico de hipertensão",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "media_files": []
  },
  "message": "Sessão criada com sucesso"
}
```

---

### GET /api/v1/sessions

**Descrição**: Lista sessões com paginação. Profissionais veem apenas as próprias.

**Auth**: Requerida

**Query Params**:
- `skip` (int, default: 0)
- `limit` (int, default: 20, máx: 100)
- `status` (string, opcional): `pending` | `processing` | `completed` | `error`

**Response 200**:
```json
{
  "total": 150,
  "items": [
    {
      "id": 42,
      "title": "Consulta Pré-natal - Semana 36",
      "patient_code": "PAC-2024-001",
      "professional_id": 1,
      "status": "completed",
      "ira_score": 65.3,
      "ira_level": "moderado",
      "score_video": 72.0,
      "score_audio": 58.0,
      "score_document": 45.0,
      "notes": null,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T11:00:00Z",
      "media_files": []
    }
  ]
}
```

---

### GET /api/v1/sessions/{session_id}

**Descrição**: Detalhe completo com arquivos de mídia.

**Auth**: Requerida

**Path Params**: `session_id` (number)

**Response 200**:
```json
{
  "id": 42,
  "title": "Consulta Pré-natal - Semana 36",
  "patient_code": "PAC-2024-001",
  "professional_id": 1,
  "status": "completed",
  "ira_score": 65.3,
  "ira_level": "moderado",
  "score_video": 72.0,
  "score_audio": 58.0,
  "score_document": 45.0,
  "notes": null,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "media_files": [
    {
      "id": 10,
      "media_type": "video",
      "filename": "consulta_01.mp4",
      "blob_url": "s3://guardia-media/...",
      "file_size_bytes": 524288000,
      "status": "analyzed",
      "analysis_score": 72.0,
      "uploaded_at": "2024-01-15T10:05:00Z"
    }
  ]
}
```

**Erros**:
- `404`: Sessão não encontrada
- `403`: Profissional tentando acessar sessão de outro

---

### PATCH /api/v1/sessions/{session_id}

**Auth**: Requerida

**Request Body** (todos opcionais):
```json
{
  "title": "Novo título",
  "notes": "Novas notas",
  "status": "completed"
}
```

**Response 200**: `SessionOut` atualizado

---

### DELETE /api/v1/sessions/{session_id}

**Auth**: Requerida | **Roles**: `admin`, `gestor`
**Response 204**: No content

---

### POST /api/v1/sessions/{session_id}/media

**Descrição**: Upload de arquivo de mídia. Inicia análise assíncrona automaticamente.

**Auth**: Requerida

**Content-Type**: `multipart/form-data`

**Form Fields**:
- `file`: arquivo binário (obrigatório)
- `media_type`: `"video"` | `"audio"` | `"document"` (obrigatório)

**Angular FormData**:
```typescript
const formData = new FormData();
formData.append('file', file, file.name);
formData.append('media_type', 'video');
// POST com Content-Type: multipart/form-data (automático com FormData)
```

**Response 202**:
```json
{
  "id": 10,
  "media_type": "video",
  "filename": "consulta_01.mp4",
  "blob_url": null,
  "file_size_bytes": 524288000,
  "status": "uploaded",
  "analysis_score": null,
  "uploaded_at": "2024-01-15T10:05:00Z"
}
```

**Limites de upload**:
- Vídeo: máx. 2000 MB
- Áudio: máx. 500 MB
- Documento: máx. 50 MB

**Erros**:
- `400`: `media_type` inválido
- `413`: Arquivo excede tamanho máximo

---

### GET /api/v1/sessions/{session_id}/analysis

**Descrição**: Retorna análise detalhada agregada (transcrição, video findings, risco).

**Auth**: Requerida

**Nota**: Retorna dados parciais se status != `completed`.

**Response 200 (completed)**:
```json
{
  "session_id": 42,
  "status": "completed",
  "transcription": {
    "full_text": "Médico: Vamos continuar. Paciente: Tá doendo...",
    "segments": [
      {
        "speaker": "Speaker_0",
        "role": "profissional",
        "start": 0.0,
        "end": 5.2,
        "text": "Vamos continuar.",
        "sentiment": "neutral",
        "sentiment_confidence": 0.78
      }
    ]
  },
  "video_findings": [
    {
      "type": "emotion",
      "timestamp_seconds": 135.5,
      "description": "Expressão de dor detectada com confiança 0.89",
      "confidence": 0.89
    }
  ],
  "video_analyses": {},
  "risk_details": {
    "video": {
      "text": "Detectadas expressões de dor em 3 momentos.",
      "key_indicators": ["dor_facial_alta_confianca"],
      "recommendation": "Revisar abordagem durante procedimentos"
    },
    "audio": {
      "text": "2 verbalizações explícitas de dor detectadas.",
      "key_indicators": ["verbalizacao_dor"],
      "recommendation": "Verificar adequação de analgesia"
    },
    "document": {
      "text": "Prontuário com 78% de completude.",
      "key_indicators": ["consentimento_ausente"],
      "recommendation": "Regularizar documentação de consentimento"
    }
  }
}
```

**Response 200 (não completed)**:
```json
{
  "session_id": 42,
  "status": "processing",
  "transcription": null,
  "video_findings": [],
  "risk_details": null
}
```

---

### DELETE /api/v1/sessions/media/{media_id}

**Auth**: Requerida
**Response 204**: No content

---

## 3. Alertas

### GET /api/v1/alerts

**Descrição**: Lista alertas com filtros.

**Auth**: Requerida

**Query Params**:
- `session_id` (number, opcional)
- `severity` (string, opcional): `"moderate"` | `"critical"`
- `unacknowledged_only` (boolean, default: false)
- `skip` (int, default: 0)
- `limit` (int, default: 50, máx: 200)

**Response 200**:
```json
{
  "total": 3,
  "items": [
    {
      "id": 5,
      "session_id": 42,
      "alert_type": "ira_critico",
      "severity": "critical",
      "title": "IGA Crítico Detectado",
      "description": "IGA = 82.3 — Risco crítico detectado na sessão",
      "ira_score": 82.3,
      "is_acknowledged": false,
      "acknowledged_by": null,
      "acknowledged_at": null,
      "email_sent": true,
      "created_at": "2024-01-15T10:45:00Z"
    }
  ]
}
```

---

### GET /api/v1/alerts/{alert_id}

**Auth**: Requerida
**Response 200**: `AlertOut` único

---

### PATCH /api/v1/alerts/{alert_id}/acknowledge

**Descrição**: Marca alerta como reconhecido.

**Auth**: Requerida

**Request Body**: Nenhum (o usuário atual é registrado automaticamente)

**Response 200**: `AlertOut` atualizado com `is_acknowledged: true`

---

## 4. Health Check

### GET /api/v1/health

**Auth**: Não requerida

**Response 200**:
```json
{
  "status": "healthy",
  "service": "core-platform",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## 5. Códigos de Status HTTP

| Código | Significado | Quando ocorre |
|---|---|---|
| 200 | OK | Requisição concluída |
| 201 | Created | Recurso criado (session, user) |
| 202 | Accepted | Upload aceito, processamento iniciado |
| 204 | No Content | Logout, delete, password change |
| 400 | Bad Request | media_type inválido |
| 401 | Unauthorized | Token ausente, inválido ou expirado |
| 403 | Forbidden | Role insuficiente |
| 404 | Not Found | Recurso não existe |
| 413 | Payload Too Large | Arquivo excede limite |
| 422 | Unprocessable Entity | Falha de validação Pydantic |
| 500 | Internal Server Error | Erro interno |
| 503 | Service Unavailable | Serviço AWS indisponível |

---

## 6. Estrutura de Erro Padrão

```json
{
  "detail": "Descrição do erro"
}
```

Para erros de validação (422):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "abc"
    }
  ]
}
```

---

## 7. IGA — Índice GuardIA de Atenção

```
Fórmula: IGA = (score_video × 0.40) + (score_audio × 0.35) + (score_document × 0.25)

Classificação:
  0.0  – 39.9 → ira_level: "baixo"    (verde)
  40.0 – 69.9 → ira_level: "moderado" (amarelo)
  70.0 – 100  → ira_level: "critico"  (vermelho)
```

---

*Documento gerado por análise do código-fonte real (backend/app/).*
