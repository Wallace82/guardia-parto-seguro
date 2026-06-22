# API_SPEC.md — GuardIA Parto Seguro

> Especificação OpenAPI — Todas as APIs dos Domínios — v1.0

---

## Convenções Gerais

- **Base URL:** `http://localhost:{porta}/api/v1`
- **Autenticação:** Bearer Token JWT no header `Authorization: Bearer <token>`
- **Content-Type:** `application/json`
- **Datas:** ISO 8601 com timezone (ex: `2024-01-15T10:30:00-03:00`)
- **IDs:** UUID v4
- **Paginação:** `?page=1&limit=20`
- **Versionamento:** URL-based (`/api/v1/`, `/api/v2/`)

---

## 1. Core Platform API — Porta 8000

### 1.1 Autenticação

#### POST `/api/v1/auth/login`
Autentica o usuário e retorna um JWT.

**Request:**
```json
{
  "email": "medico@hospital.com",
  "password": "senha_segura"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "medico@hospital.com",
    "full_name": "Dr. João Silva",
    "role": "profissional"
  }
}
```

**Response 401:**
```json
{
  "detail": "Credenciais inválidas"
}
```

---

#### POST `/api/v1/auth/refresh`
Renova o token de acesso.

**Request:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

---

### 1.2 Sessões Clínicas

#### POST `/api/v1/sessions`
Cria uma nova sessão clínica.

**Request:**
```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440001",
  "session_type": "consulta",
  "session_date": "2024-01-15T10:00:00-03:00",
  "unit_name": "Maternidade Santa Maria",
  "metadata": {
    "gestational_age_weeks": 36,
    "high_risk": true
  }
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "created",
  "patient_id": "550e8400-e29b-41d4-a716-446655440001",
  "professional_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_type": "consulta",
  "session_date": "2024-01-15T10:00:00-03:00",
  "unit_name": "Maternidade Santa Maria",
  "created_at": "2024-01-15T09:55:00-03:00"
}
```

---

#### GET `/api/v1/sessions/{session_id}`
Retorna detalhes e status completo da sessão.

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "completed",
  "patient_id": "550e8400-e29b-41d4-a716-446655440001",
  "media": [
    {
      "id": "...",
      "media_type": "video",
      "original_filename": "consulta_01.mp4",
      "status": "analyzed"
    }
  ],
  "ira_result": {
    "ira_score": 72.5,
    "risk_level": "critico",
    "calculated_at": "2024-01-15T10:45:00-03:00"
  },
  "alerts": [
    {
      "id": "...",
      "severity": "critical",
      "alert_type": "expressao_sofrimento",
      "description": "Detectadas expressões de dor intensa em 4 frames (02:15–02:30)",
      "is_acknowledged": false
    }
  ]
}
```

---

#### POST `/api/v1/sessions/{session_id}/media`
Faz upload de uma mídia para a sessão.

**Request:** `multipart/form-data`
```
file: <arquivo_binário>
media_type: "video" | "audio" | "document"
```

**Response 202:**
```json
{
  "media_id": "550e8400-e29b-41d4-a716-446655440010",
  "status": "uploaded",
  "blob_url": "s3://guardia-parto-seguro/media/session_id/arquivo.mp4",
  "processing_started": true,
  "message": "Análise iniciada em background"
}
```

---

#### GET `/api/v1/alerts`
Lista alertas com filtros.

**Query params:** `?severity=critical&is_acknowledged=false&page=1&limit=20`

**Response 200:**
```json
{
  "total": 5,
  "page": 1,
  "limit": 20,
  "items": [
    {
      "id": "...",
      "session_id": "...",
      "severity": "critical",
      "alert_type": "ira_critico",
      "description": "IRA = 82.3 — Risco crítico detectado na sessão",
      "triggered_at": "2024-01-15T10:45:00-03:00",
      "is_acknowledged": false
    }
  ]
}
```

---

#### PATCH `/api/v1/alerts/{alert_id}/acknowledge`
Reconhece um alerta.

**Request:**
```json
{
  "acknowledgment_note": "Caso verificado. Encaminhado para assistente social."
}
```

**Response 200:**
```json
{
  "id": "...",
  "is_acknowledged": true,
  "acknowledged_at": "2024-01-15T11:00:00-03:00",
  "acknowledged_by": "Dr. João Silva"
}
```

---

## 2. Video Analysis API — Porta 8001

#### POST `/api/v1/video/analyze`
Inicia análise de vídeo.

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "media_id": "550e8400-e29b-41d4-a716-446655440010",
  "blob_url": "s3://guardia-parto-seguro/media/video.mp4",
  "options": {
    "analyze_emotions": true,
    "analyze_pose": true,
    "detect_objects": true,
    "detect_bleeding": true,
    "frame_sample_rate": 1.0
  }
}
```

**Response 202:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440020",
  "status": "queued",
  "estimated_duration_seconds": 900
}
```

---

#### GET `/api/v1/video/results/{session_id}`
Retorna resultado completo da análise de vídeo.

**Response 200:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "job_id": "550e8400-e29b-41d4-a716-446655440020",
  "status": "completed",
  "ira_score": 68.4,
  "components": {
    "emotion_score": 75.2,
    "pose_score": 60.1,
    "object_risk_score": 45.0,
    "bleeding_score": 0.0
  },
  "total_frames": 54000,
  "analyzed_frames": 1800,
  "key_findings": [
    {
      "type": "emotion",
      "timestamp_seconds": 135.5,
      "description": "Expressão de dor detectada com confiança 0.89",
      "confidence": 0.89
    }
  ],
  "completed_at": "2024-01-15T10:30:00-03:00"
}
```

---

## 3. Audio Analysis API — Porta 8002

#### POST `/api/v1/audio/analyze`
Inicia análise de áudio.

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "media_id": "550e8400-e29b-41d4-a716-446655440011",
  "blob_url": "s3://guardia-parto-seguro/media/audio.wav",
  "language": "pt-BR",
  "options": {
    "speaker_diarization": true,
    "sentiment_analysis": true,
    "ner_extraction": true,
    "risk_keyword_detection": true
  }
}
```

**Response 202:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440021",
  "status": "queued"
}
```

---

#### GET `/api/v1/audio/results/{session_id}`
Retorna resultado completo com transcrição.

**Response 200:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "ira_score": 55.2,
  "transcription": {
    "full_text": "Médico: Vamos fazer o procedimento agora. Paciente: Tá doendo muito, por favor...",
    "language": "pt-BR",
    "duration_seconds": 1823.5,
    "segments": [
      {
        "speaker": "Speaker_0",
        "role": "profissional",
        "start": 0.0,
        "end": 5.2,
        "text": "Vamos fazer o procedimento agora.",
        "sentiment": "neutral",
        "sentiment_confidence": 0.78
      },
      {
        "speaker": "Speaker_1",
        "role": "paciente",
        "start": 5.8,
        "end": 10.1,
        "text": "Tá doendo muito, por favor.",
        "sentiment": "negative",
        "sentiment_confidence": 0.94
      }
    ]
  },
  "risk_keywords": [
    {
      "keyword": "tá doendo muito",
      "category": "dor",
      "timestamp_seconds": 5.8,
      "speaker": "Speaker_1",
      "severity": "high"
    }
  ],
  "clinical_entities": [
    {"text": "procedimento", "category": "Procedimento", "confidence": 0.88}
  ]
}
```

---

## 4. Document Analysis API — Porta 8003

#### POST `/api/v1/documents/analyze`
Inicia análise documental.

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "media_id": "550e8400-e29b-41d4-a716-446655440012",
  "blob_url": "s3://guardia-parto-seguro/media/prontuario.pdf",
  "document_type": "prontuario"
}
```

**Response 200:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "ira_score": 35.0,
  "document_type": "prontuario",
  "extracted_fields": {
    "patient_name_hash": "abc123...",
    "medical_record": "HC-2024-001",
    "diagnosis_cid10": ["O26.8", "Z34.3"],
    "procedures": ["Exame obstétrico", "Cardiotocografia"],
    "medications": [
      {"name": "Ocitocina", "dose": "5 UI", "route": "IV"}
    ],
    "professional_signature": true,
    "professional_crm": "CRM-SP 123456",
    "attendance_date": "2024-01-15",
    "consent_present": false
  },
  "completeness_score": 78.5,
  "consistency_checks": [
    {
      "check": "consent_present",
      "passed": false,
      "severity": "high",
      "detail": "Consentimento informado ausente para procedimento invasivo"
    },
    {
      "check": "professional_signature",
      "passed": true,
      "severity": "none",
      "detail": "Assinatura e CRM presentes"
    }
  ]
}
```

---

## 5. Risk Correlation API — Porta 8004

#### POST `/api/v1/risk/correlate`
Calcula o IRA composto.

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "patient_id": "550e8400-e29b-41d4-a716-446655440001",
  "video_score": 68.4,
  "audio_score": 55.2,
  "document_score": 35.0
}
```

**Response 200:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "ira_score": 56.3,
  "risk_level": "moderado",
  "calculation": {
    "video_contribution": 27.36,
    "audio_contribution": 19.32,
    "document_contribution": 8.75,
    "weights_applied": {
      "video": 0.40,
      "audio": 0.35,
      "document": 0.25
    }
  },
  "justifications": {
    "video": {
      "text": "Detectadas expressões de dor em 3 momentos distintos. Postura de sofrimento em 15% dos frames analisados.",
      "key_indicators": ["dor_facial_alta_confianca", "postura_defensiva"],
      "recommendation": "Revisar abordagem durante procedimentos"
    },
    "audio": {
      "text": "2 verbalizações explícitas de dor detectadas. Sentimento predominantemente negativo nos segmentos da paciente (0.82).",
      "key_indicators": ["verbalizacao_dor", "sentimento_negativo_alto"],
      "recommendation": "Verificar adequação de analgesia"
    },
    "document": {
      "text": "Prontuário com 78% de completude. Ausência de consentimento informado identificada.",
      "key_indicators": ["consentimento_ausente"],
      "recommendation": "Regularizar documentação de consentimento"
    }
  },
  "calculated_at": "2024-01-15T10:46:00-03:00"
}
```

---

## 6. Report API — Porta 8005

#### POST `/api/v1/reports/generate`
Gera relatório da sessão.

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440002",
  "report_type": "session",
  "report_format": "pdf",
  "include_transcription": true,
  "include_key_frames": true
}
```

**Response 202:**
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440030",
  "status": "generating",
  "estimated_seconds": 30
}
```

---

#### GET `/api/v1/reports/{report_id}`
Download ou URL do relatório.

**Response 200:**
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440030",
  "title": "Relatório de Sessão — 15/01/2024",
  "report_type": "session",
  "report_format": "pdf",
  "download_url": "https://guardia-parto-seguro.s3.amazonaws.com/reports/report.pdf?X-Amz-Algorithm=...",
  "file_size_bytes": 245760,
  "file_hash_sha256": "a1b2c3d4...",
  "generated_at": "2024-01-15T10:48:00-03:00",
  "expires_at": "2024-01-16T10:48:00-03:00"
}
```

---

## 7. Security API — Porta 8006

#### GET `/api/v1/audit`
Recupera o log de auditoria imutável (requer role `auditor` ou `admin`).

**Response 200:**
```json
{
  "total": 125,
  "items": [
    {
      "timestamp": "2024-01-15T10:30:00-03:00",
      "actor_id": "550e8400-e29b-41d4-a716-446655440000",
      "role": "medico",
      "action": "READ_SESSION",
      "resource_type": "session",
      "resource_id": "550e8400-e29b-41d4-a716-446655440002",
      "ip_address": "192.168.1.50"
    }
  ]
}
```

---

## 8. AWS Integration API — Porta 8007

#### POST `/api/v1/s3/upload-url`
Retorna uma Pre-signed URL para fazer upload direto e seguro para o Amazon S3.

**Request:**
```json
{
  "file_name": "prontuario_teste.pdf",
  "bucket_type": "media",
  "expiration_seconds": 3600,
  "content_type": "application/pdf"
}
```

**Response 200:**
```json
{
  "url": "https://guardia-parto-seguro-media-dev.s3.amazonaws.com/prontuario_teste.pdf?X-Amz-Signature=...",
  "file_name": "prontuario_teste.pdf",
  "expiration_seconds": 3600
}
```

---

#### POST `/api/v1/textract/analyze`
Inicia a análise de extração de texto (OCR assíncrono) de um documento já armazenado no S3.

**Request:**
```json
{
  "file_name": "prontuario_teste.pdf",
  "bucket_type": "media"
}
```

**Response 200:**
```json
{
  "job_id": "b1b2c3d4-e5f6...",
  "status": "IN_PROGRESS"
}
```

---

#### GET `/api/v1/textract/results/{job_id}`
Recupera o status e o resultado do job de análise do Textract.

**Response 200 (Em progresso):**
```json
{
  "job_id": "b1b2c3d4-e5f6...",
  "status": "IN_PROGRESS",
  "extracted_text": null,
  "blocks": null
}
```

**Response 200 (Concluído):**
```json
{
  "job_id": "b1b2c3d4-e5f6...",
  "status": "SUCCEEDED",
  "extracted_text": "Texto extraído do documento médico...\nLinha 2...\n",
  "blocks": [
    {
      "block_type": "LINE",
      "text": "Texto extraído do documento médico...",
      "confidence": 99.8
    }
  ]
}
```

---

## 9. OpenAPI / Swagger

Cada serviço expõe automaticamente sua documentação Swagger em:

| Serviço | Swagger UI | OpenAPI JSON |
|---|---|---|
| Core API | http://localhost:8000/docs | http://localhost:8000/openapi.json |
| Video API | http://localhost:8001/docs | http://localhost:8001/openapi.json |
| Audio API | http://localhost:8002/docs | http://localhost:8002/openapi.json |
| Document API | http://localhost:8003/docs | http://localhost:8003/openapi.json |
| Risk API | http://localhost:8004/docs | http://localhost:8004/openapi.json |
| Report API | http://localhost:8005/docs | http://localhost:8005/openapi.json |
| Security API | http://localhost:8006/docs | http://localhost:8006/openapi.json |
| AWS API | http://localhost:8007/docs | http://localhost:8007/openapi.json |

---

## 10. Códigos de Status HTTP

| Código | Significado |
|---|---|
| 200 | OK — requisição concluída com sucesso |
| 201 | Created — recurso criado com sucesso |
| 202 | Accepted — processamento iniciado em background |
| 400 | Bad Request — dados de entrada inválidos |
| 401 | Unauthorized — token ausente ou inválido |
| 403 | Forbidden — permissão insuficiente |
| 404 | Not Found — recurso não encontrado |
| 409 | Conflict — conflito de estado (ex: sessão já processada) |
| 413 | Payload Too Large — arquivo excede tamanho máximo |
| 422 | Unprocessable Entity — falha de validação Pydantic |
| 429 | Too Many Requests — rate limit atingido |
| 500 | Internal Server Error — erro interno |
| 503 | Service Unavailable — serviço AWS indisponível |
