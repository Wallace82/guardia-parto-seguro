# DOMAINS.md — GuardIA Parto Seguro

> Definição Completa de Domínios — v1.0

---

## Visão Geral dos Domínios

O sistema é composto por **10 domínios independentes**. Cada domínio possui:
- Banco de dados próprio (schema isolado)
- API pública versionada
- Eventos publicados e consumidos
- Estrutura de pastas dedicada

Nenhum domínio acessa diretamente o banco de outro. Toda comunicação ocorre via APIs REST.

---

## Domínio 1 — Core Platform

### Objetivo
Prover a infraestrutura central do sistema: autenticação, gerenciamento de sessões, motor de alertas e log de auditoria.

### Responsabilidades
- Autenticação e autorização (JWT + RBAC)
- Gerenciamento de usuários e papéis
- Criação e controle de sessões clínicas
- Motor de alertas e notificações
- Log de auditoria imutável
- Orquestração do fluxo multimodal

### Limites (Boundaries)
- ✅ Gerencia usuários, sessões e alertas
- ✅ Roteia requisições para os demais domínios
- ❌ Não processa vídeo, áudio ou documentos diretamente
- ❌ Não calcula IRA

### Dependências
- Security Domain (Auth, LGPD, Audit)
- Cloud Domain (Armazenamento Blob)
- Banco: `core_db` (PostgreSQL)

### APIs Públicas

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/auth/login` | Autenticação de usuário |
| POST | `/api/v1/auth/refresh` | Renovação de token |
| GET | `/api/v1/sessions` | Lista sessões do usuário |
| POST | `/api/v1/sessions` | Cria nova sessão clínica |
| GET | `/api/v1/sessions/{id}` | Detalhe da sessão e status |
| POST | `/api/v1/sessions/{id}/media` | Upload de mídia para sessão |
| GET | `/api/v1/alerts` | Lista alertas ativos |
| PATCH | `/api/v1/alerts/{id}/acknowledge` | Reconhece um alerta |
| GET | `/api/v1/health` | Healthcheck |

### Eventos Publicados
- `session.created` — Sessão clínica criada
- `session.media_uploaded` — Mídia adicionada à sessão
- `session.processing_completed` — Todos os domínios concluíram análise
- `alert.triggered` — Alerta disparado
- `alert.acknowledged` — Alerta reconhecido

### Eventos Consumidos
- `video.analysis_completed` — Vem do Video Domain
- `audio.analysis_completed` — Vem do Audio Domain
- `document.analysis_completed` — Vem do Document Domain
- `risk.ira_calculated` — Vem do Risk Domain

### Banco de Dados: `core_db`
Tabelas principais: `users`, `roles`, `sessions`, `session_media`, `alerts`, `audit_logs`

### Estrutura de Pastas
```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── sessions/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── alerts/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   └── orchestrator/
│       ├── orchestrator.py
│       └── domain_client.py
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Domínio 2 — Video Analysis Domain

### Objetivo
Processar vídeos clínicos para detectar indicadores de risco assistencial: expressões de sofrimento, postura, sangramento e objetos de risco.

### Responsabilidades
- Receber e armazenar vídeos temporariamente
- Extração de frames e pré-processamento local (OpenCV)
- Análise de expressões faciais e emoções de forma local (DeepFace)
- Análise de postura corporal de forma local (MediaPipe)
- Detecção de objetos de forma local (YOLOv8)
- Detecção de sangramento por análise de cor (OpenCV)
- Identificação de pessoas (face_recognition)
- Geração de score de contribuição para o IRA

### Limites
- ✅ Processa apenas arquivos de vídeo
- ✅ Retorna scores e alertas para o Core
- ❌ Não acessa banco de áudio ou documentos
- ❌ Não calcula o IRA final

### Dependências
- Cloud Integration Domain (Upload e Storage seguro)
- Core Platform (recebe token de sessão)
- Banco: `video_db` (PostgreSQL)

### APIs Públicas

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/video/analyze` | Inicia análise de vídeo |
| GET | `/api/v1/video/jobs/{job_id}` | Status do job de análise |
| GET | `/api/v1/video/results/{session_id}` | Resultado da análise |
| GET | `/api/v1/video/health` | Healthcheck |

### Eventos Publicados
- `video.analysis_started` — Início do processamento
- `video.analysis_completed` — Análise concluída com sucesso
- `video.analysis_failed` — Falha no processamento

### Eventos Consumidos
- `session.media_uploaded` (tipo vídeo) — Inicia o processamento

### Banco de Dados: `video_db`
Tabelas: `video_jobs`, `video_results`, `frame_analyses`, `face_detections`, `pose_analyses`, `object_detections`

### Estrutura de Pastas
```
video-domain/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── video/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── analyzers/
│   │   ├── deepface_analyzer.py
│   │   ├── mediapipe_analyzer.py
│   │   ├── yolo_analyzer.py
│   │   ├── opencv_analyzer.py
│   │   └── face_recognition_analyzer.py
│   ├── pipeline/
│   │   ├── video_pipeline.py
│   │   └── frame_extractor.py
│   └── scoring/
│       └── ira_video_scorer.py
├── models/
│   └── yolov8n.pt
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Domínio 3 — Audio Analysis Domain

### Objetivo
Transcrever e analisar áudios de consultas para detectar indicadores linguísticos e prosódicos de sofrimento, ameaça e risco obstétrico.

### Responsabilidades
- Receber e armazenar arquivos de áudio
- Transcrição via Azure Speech (STT com speaker diarization)
- Análise de sentimento (Azure AI Language)
- Extração de entidades clínicas (NER)
- Detecção de verbalizações de risco (keywords, padrões)
- Análise de tom e prosódia
- Geração de score de contribuição para o IRA

### Limites
- ✅ Processa apenas arquivos de áudio
- ❌ Não processa vídeo ou documentos
- ❌ Não calcula o IRA final

### Dependências
- Cloud Integration Domain (para STS, NLP e Storage no Azure)
- Banco: `audio_db` (PostgreSQL)

### APIs Públicas

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/audio/analyze` | Inicia análise de áudio |
| GET | `/api/v1/audio/jobs/{job_id}` | Status do job |
| GET | `/api/v1/audio/results/{session_id}` | Resultado com transcrição |
| GET | `/api/v1/audio/health` | Healthcheck |

### Eventos Publicados
- `audio.analysis_started`
- `audio.analysis_completed`
- `audio.analysis_failed`

### Banco de Dados: `audio_db`
Tabelas: `audio_jobs`, `transcriptions`, `speaker_segments`, `sentiment_results`, `ner_results`, `risk_keywords`, `audio_scores`

### Estrutura de Pastas
```
audio-domain/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── audio/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── analyzers/
│   │   ├── azure_speech_analyzer.py
│   │   ├── azure_language_analyzer.py
│   │   ├── sentiment_analyzer.py
│   │   ├── ner_analyzer.py
│   │   └── prosody_analyzer.py
│   └── scoring/
│       └── ira_audio_scorer.py
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Domínio 4 — Document Analysis Domain

### Objetivo
Processar documentos médicos (prontuários, exames, consentimentos) para extrair informações estruturadas e detectar inconsistências.

### Responsabilidades
- Receber e armazenar documentos
- OCR e extração de texto (Azure Document Intelligence)
- Parsing de campos obstétricos
- Validação de completude e consistência
- Verificação de consentimento informado
- Geração de score de contribuição para o IRA

### Dependências
- Cloud Integration Domain (para OCR no Azure)
- Banco: `document_db` (PostgreSQL)

### APIs Públicas

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/documents/analyze` | Inicia análise documental |
| GET | `/api/v1/documents/jobs/{job_id}` | Status do job |
| GET | `/api/v1/documents/results/{session_id}` | Resultado estruturado |
| GET | `/api/v1/documents/health` | Healthcheck |

### Banco de Dados: `document_db`
Tabelas: `document_jobs`, `document_results`, `extracted_fields`, `consistency_checks`, `consent_records`

### Estrutura de Pastas
```
document-domain/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── documents/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── analyzers/
│   │   ├── azure_doc_analyzer.py
│   │   ├── field_extractor.py
│   │   ├── consistency_checker.py
│   │   └── consent_validator.py
│   └── scoring/
│       └── ira_document_scorer.py
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Domínio 5 — Risk Correlation Domain

### Objetivo
Receber os scores parciais dos três domínios de análise e calcular o IRA (Índice de Risco Assistencial) composto, com justificativas e histórico.

### Responsabilidades
- Receber scores de vídeo, áudio e documentos
- Aplicar modelo de ponderação (40%/35%/25%)
- Calcular o IRA final (0–100)
- Classificar o nível de risco (Baixo/Moderado/Crítico)
- Gerar justificativas textuais por componente
- Manter histórico de IRA por paciente
- Calcular tendências temporais

### APIs Públicas

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/risk/correlate` | Calcula IRA com base nos scores |
| GET | `/api/v1/risk/history/{patient_id}` | Histórico de IRA da paciente |
| GET | `/api/v1/risk/session/{session_id}` | IRA da sessão |
| GET | `/api/v1/risk/health` | Healthcheck |

### Banco de Dados: `risk_db`
Tabelas: `ira_calculations`, `risk_components`, `risk_justifications`, `patient_risk_history`

### Estrutura de Pastas
```
risk-domain/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── risk/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── calculators/
│   │   ├── ira_calculator.py
│   │   ├── weight_model.py
│   │   └── trend_analyzer.py
│   └── classifiers/
│       └── risk_classifier.py
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Domínio 6 — Reporting Domain

### Objetivo
Gerar relatórios especializados em PDF e Excel a partir dos dados consolidados da sessão e do IRA.

### Responsabilidades
- Gerar relatório completo de sessão (PDF)
- Gerar relatório executivo (Excel)
- Gerar relatório de auditoria (PDF imutável com hash)
- Armazenar relatórios no Azure Blob Storage
- Disponibilizar URLs de download

### APIs Públicas

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/v1/reports/generate` | Gera relatório da sessão |
| GET | `/api/v1/reports/{report_id}` | Download do relatório |
| GET | `/api/v1/reports/session/{session_id}` | Lista relatórios da sessão |
| GET | `/api/v1/reports/health` | Healthcheck |

### Banco de Dados: `report_db`
Tabelas: `reports`, `report_sections`, `report_attachments`

### Estrutura de Pastas
```
report-domain/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── reports/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── generators/
│   │   ├── pdf_generator.py
│   │   ├── excel_generator.py
│   │   └── audit_report_generator.py
│   └── templates/
│       ├── session_report.html
│       └── audit_report.html
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Domínio 7 — Dashboard Domain

### Objetivo
Fornecer interface visual multimodal para monitoramento em tempo real, histórico de IRA e central de alertas.

### Responsabilidades
- Exibir dashboard de sessão com IRA e alertas
- Exibir mapa de calor temporal do IRA
- Sincronizar transcrição com vídeo
- Exibir histórico de IRA da paciente
- Central de alertas com filtros
- Download de relatórios

### Dependências
- Core Platform API
- Risk Domain API
- Report Domain API

### Estrutura de Pastas
```
frontend/
├── app.py
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Sessions.py
│   ├── 3_Alerts.py
│   ├── 4_Reports.py
│   └── 5_Admin.py
├── components/
│   ├── ira_gauge.py
│   ├── video_player.py
│   ├── transcript_viewer.py
│   ├── alert_card.py
│   └── risk_heatmap.py
├── services/
│   ├── api_client.py
│   └── auth_service.py
├── assets/
│   └── styles.css
├── Dockerfile
└── requirements.txt
```

---

## Domínio 8 — DevOps Domain

### Objetivo
Prover toda a infraestrutura de orquestração via containers puramente para execução local e demonstração do Tech Challenge.

### Responsabilidades
- Configuração do Docker Compose para ambiente local
- Scripts de setup, migrações locais e gestão de serviços
- Gestão de chaves da Azure limitadas ao `.env` local

### Estrutura de Pastas
```
devops/
├── docker-compose.yml
├── docker-compose.override.yml
├── nginx/
│   └── nginx.conf
├── scripts/
│   ├── setup_local.sh
│   ├── deploy_azure.sh
│   └── seed_db.py
└── monitoring/
    ├── alerts.json
    └── dashboards.json
```

---

## Domínio 9 — Cloud Integration Domain

### Objetivo
Atuar como ponte para os serviços cognitivos gerenciados (Azure Speech, Language, Document Intelligence), cumprindo a exigência de integração com nuvem do Tech Challenge.

### Responsabilidades
- Roteamento de requisições para o Azure Speech e AI Language (consumidos pelo Domínio de Áudio)
- Roteamento para Azure Document Intelligence (consumido pelo Domínio de Documentos)
- (Opcional) Integração avançada com Azure Blob e Azure Monitor se as demonstrações exigirem

### Limites
- ✅ Ponto único de saída da VPC para a rede Microsoft
- ❌ Não analisa regras de negócio (apenas passa para frente)

### Dependências
- Azure Blob Storage, Azure Speech, Azure Language, Azure Doc Intel, Azure Monitor
- Banco: `cloud_db` (PostgreSQL - Histórico de chamadas para nuvem e custos)

### Estrutura de Pastas
```
cloud-domain/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── storage/
│   ├── speech/
│   ├── document/
│   └── telemetry/
├── Dockerfile
└── requirements.txt
```

---

## Domínio 10 — Security Domain

### Objetivo
Garantir total conformidade com a LGPD e políticas Zero Trust. 

### Responsabilidades
- Gestão de Identidade e Autenticação (JWT) e RBAC
- Criptografia e decriptação em tempo real (AES-256)
- Anonimização de dados (Hash unidirecional, mascaramento)
- Gestão de segredos via Azure Key Vault
- Audit Logger (Trilha de auditoria imutável)

### Limites
- ✅ Intercepta requisições no API Gateway para checar tokens
- ✅ Realiza mascaramento de PII (Personally Identifiable Information) antes da persistência no Core
- ❌ Não gerencia a sessão clínica

### Dependências
- Azure Key Vault
- Banco: `security_db` (PostgreSQL - Auth, Tokens, Access History, Consentimentos)

### Estrutura de Pastas
```
security-domain/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth/
│   ├── rbac/
│   ├── crypto/
│   ├── audit/
│   └── lgpd/
├── Dockerfile
└── requirements.txt
```
