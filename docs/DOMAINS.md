# DOMAINS.md — GuardIA Parto Seguro

> Definição Completa de Domínios — v2.0

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
- Autenticação e autorização (JWT + IAM RBAC)
- Gerenciamento de usuários e papéis
- Criação e controle de sessões clínicas
- Motor de alertas e notificações
- Log de auditoria imutável
- Orquestração do fluxo multimodal

### Limites (Boundaries)
- ✅ Gerencia usuários, sessões e alertas
- ✅ Roteia requisições para os demais domínios
- ❌ Não processa vídeo, áudio ou documentos diretamente
- ❌ Não calcula IGA

### Dependências
- Security Domain (Auth, LGPD, Audit)
- AWS Integration Domain (Armazenamento S3)
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
│   ├── sessions/
│   ├── alerts/
│   └── orchestrator/
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## Domínio 2 — Video Analysis Domain

### Objetivo
Processar vídeos clínicos de forma estritamente local (MVP) para detectar indicadores de risco assistencial: expressões de sofrimento, postura, sangramento e objetos de risco.

### Responsabilidades
- Receber e armazenar vídeos temporariamente
- Extração de frames e pré-processamento local (OpenCV)
- Análise de expressões faciais e emoções de forma local (DeepFace)
- Análise de postura corporal de forma local (MediaPipe)
- Detecção de objetos de forma local (YOLOv8)
- Detecção de sangramento por análise de cor (OpenCV)
- Identificação de pessoas (face_recognition)
- Geração de score de contribuição para o IGA

### Limites
- ✅ Processa apenas arquivos de vídeo localmente
- ✅ Retorna scores e alertas para o Core
- ❌ Não acessa banco de áudio ou documentos

### Dependências
- AWS Integration Domain (Upload e Storage seguro em S3)
- Core Platform (recebe token de sessão)
- Banco: `video_db` (PostgreSQL)

### Estrutura de Pastas
```
video-domain/
├── app/
│   ├── analyzers/
│   │   ├── deepface_analyzer.py
│   │   ├── mediapipe_analyzer.py
│   │   ├── yolo_analyzer.py
│   │   ├── opencv_analyzer.py
│   │   └── face_recognition_analyzer.py
│   └── ...
├── models/
│   └── yolov8n.pt
└── Dockerfile
```

---

## Domínio 3 — Audio Analysis Domain

### Objetivo
Transcrever e analisar áudios de consultas delegando o processamento para AWS, visando detectar indicadores linguísticos e prosódicos de sofrimento, ameaça e risco obstétrico.

### Responsabilidades
- Receber e armazenar arquivos de áudio
- Transcrição via Amazon Transcribe (STT com speaker diarization)
- Análise de sentimento (Amazon Comprehend)
- Extração de entidades clínicas (NER via Amazon Comprehend)
- Detecção de verbalizações de risco (keywords, padrões)
- Análise de tom e prosódia
- Geração de score de contribuição para o IGA

### Dependências
- AWS Integration Domain (para Transcribe, Comprehend e Storage no S3)
- Banco: `audio_db` (PostgreSQL)

### Estrutura de Pastas
```
audio-domain/
├── app/
│   ├── analyzers/
│   │   ├── aws_transcribe_analyzer.py
│   │   ├── aws_comprehend_analyzer.py
│   │   ├── sentiment_analyzer.py
│   │   ├── ner_analyzer.py
│   │   └── prosody_analyzer.py
│   └── ...
└── Dockerfile
```

---

## Domínio 4 — Document Analysis Domain

### Objetivo
Processar documentos médicos (prontuários, exames, consentimentos) delegando para a AWS a extração de informações estruturadas e detecção de inconsistências.

### Responsabilidades
- Receber e armazenar documentos
- OCR e extração de texto (Amazon Textract)
- Parsing de campos obstétricos
- Validação de completude e consistência
- Verificação de consentimento informado
- Geração de score de contribuição para o IGA

### Dependências
- AWS Integration Domain (para OCR via Textract)
- Banco: `document_db` (PostgreSQL)

### Estrutura de Pastas
```
document-domain/
├── app/
│   ├── analyzers/
│   │   ├── aws_textract_analyzer.py
│   │   ├── field_extractor.py
│   │   ├── consistency_checker.py
│   │   └── consent_validator.py
│   └── ...
└── Dockerfile
```

---

## Domínio 5 — Risk Correlation Domain

### Objetivo
Receber os scores parciais dos três domínios de análise e calcular o IGA (Índice GuardIA de Atenção) composto, com justificativas e histórico.

### Responsabilidades
- Receber scores de vídeo, áudio e documentos
- Aplicar modelo de ponderação (40%/35%/25%)
- Calcular o IGA final (0–100)
- Classificar o nível de risco (Baixo/Moderado/Crítico)
- Gerar justificativas textuais por componente
- Manter histórico de IGA por paciente

### Banco de Dados: `risk_db`
Tabelas: `ira_calculations`, `risk_components`, `risk_justifications`, `patient_risk_history`

---

## Domínio 6 — Reporting Domain

### Objetivo
Gerar relatórios especializados em PDF e Excel a partir dos dados consolidados da sessão e do IGA.

### Responsabilidades
- Gerar relatório completo de sessão (PDF)
- Gerar relatório executivo (Excel)
- Gerar relatório de auditoria (PDF imutável com hash)
- Armazenar relatórios no Amazon S3 (via AWS Integration)
- Disponibilizar URLs pré-assinadas para download

### Banco de Dados: `report_db`
Tabelas: `reports`, `report_sections`, `report_attachments`

---

## Domínio 7 — Dashboard Domain

### Objetivo
Fornecer interface visual multimodal (Streamlit) para monitoramento em tempo real, histórico de IGA e central de alertas.

---

## Domínio 8 — DevOps Domain

### Objetivo
Prover toda a infraestrutura de orquestração via containers para os diferentes ambientes de execução, incluindo deploy na AWS.

### Responsabilidades
- Configuração do Docker Compose para ambientes LOCAL e DEV.
- Pipelines de CI/CD para deploy nos ambientes HML e PRD (AWS ECS Fargate).
- Scripts de setup de infraestrutura em nuvem (IaC - Terraform/CloudFormation).

### Estrutura de Pastas
```
infrastructure/
├── terraform/
│   ├── vpc/
│   ├── ecs/
│   ├── rds/
│   └── s3/
environments/
├── local/
│   └── docker-compose.yml
├── dev/
├── hml/
└── prd/
```

---

## Domínio 9 — AWS Integration Domain

### Objetivo
Atuar como hub centralizado de integração para os serviços cognitivos e de infraestrutura gerenciados da AWS.

### Responsabilidades
- Roteamento de requisições para o Amazon Transcribe e Amazon Comprehend (consumidos pelo Domínio de Áudio)
- Roteamento para Amazon Textract (consumido pelo Domínio de Documentos)
- Integração de armazenamento com Amazon S3
- Integração de auditoria e logs com Amazon CloudWatch
- Integração com Amazon Bedrock (opcional para IA Generativa avançada)
- Gestão de chaves dinâmicas via AWS Secrets Manager

### Limites
- ✅ Ponto único de saída da VPC local para a rede AWS
- ❌ Não analisa regras de negócio

### Dependências
- Amazon S3, Amazon Transcribe, Amazon Comprehend, Amazon Textract, Amazon CloudWatch, AWS Secrets Manager, Amazon Bedrock.
- Banco: `aws_db` (PostgreSQL - Histórico de chamadas para nuvem e custos)

### Estrutura de Pastas
```
aws-domain/
├── app/
│   ├── storage/ (S3)
│   ├── speech/ (Transcribe)
│   ├── language/ (Comprehend)
│   ├── document/ (Textract)
│   ├── telemetry/ (CloudWatch)
│   └── secrets/ (Secrets Manager)
└── Dockerfile
```

---

## Domínio 10 — Security Domain

### Objetivo
Garantir total conformidade com a LGPD e políticas de acesso AWS IAM e Zero Trust.

### Responsabilidades
- Gestão de Identidade, Autenticação e IAM (Identity and Access Management)
- Criptografia de dados em repouso (S3 Encryption) e em trânsito (HTTPS/TLS)
- Anonimização de dados pessoais antes de armazenamento permanente (Hash unidirecional, mascaramento)
- Integração com AWS Secrets Manager para credenciais dinâmicas
- Audit Logger (Trilha de auditoria enviada para o Amazon CloudWatch Logs)

### Limites
- ✅ Intercepta requisições no API Gateway para checar tokens e permissões
- ✅ Realiza mascaramento de PII (Personally Identifiable Information)
- ❌ Não gerencia a sessão clínica

### Dependências
- AWS Secrets Manager, Amazon CloudWatch
- Banco: `security_db` (PostgreSQL)

### Estrutura de Pastas
```
security-domain/
├── app/
│   ├── auth/
│   ├── iam/
│   ├── crypto/
│   ├── audit/
│   └── lgpd/
└── Dockerfile
```
