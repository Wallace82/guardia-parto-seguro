# TEAM_PLAN.md — GuardIA Parto Seguro

> Plano da Equipe, Responsabilidades, Agentes de IA e Estratégia Git — v2.0  

---

## 1. Organização da Equipe

### 👨‍💻 Wallace Gomes (Dev 1) — Core Platform & DevOps

**Foco:** `backend/` + `infra/`
**Status:** 🟡 Em progresso

#### Tarefas
- [x] Configurar repositório Git com branch strategy e proteções
- [x] Criar `.env.example` e documentação de setup
- [x] Criar `.gitignore` completo para projeto Python
- [x] Criar template de Pull Request (`.github/pull_request_template.md`)
- [x] Configurar estrutura base do API Gateway (FastAPI): `main.py` + `config.py`
- [x] Configurar Docker Compose completo (MVP Local)
- [x] Implementar auth JWT e gerenciamento de sessões
- [x] Implementar módulo de orquestração multimodal
- [x] Configurar banco `core_db` com Alembic migrations
- [x] Implementar engine de alertas e notificações
- [x] Criar healthchecks e endpoints base

---

### 👩‍💻 Paulo Roberto Gonçalves (Dev 2) — Video AI & Audio AI

**Foco:** `video-domain/` + `audio-domain/`

#### Tarefas

**Video Domain (MVP Local):**
- [x] Configurar serviço FastAPI de vídeo
- [x] Implementar pipeline de extração de frames (OpenCV)
- [x] Integrar DeepFace para análise de emoções
- [x] Integrar MediaPipe para pose estimation
- [x] Integrar YOLOv8 para detecção de objetos
- [x] Implementar detecção de sangramento (OpenCV HSV)
- [x] Implementar IGA scorer de vídeo

**Audio Domain (Integração AWS):**
- [x] Configurar serviço FastAPI de áudio
- [x] Integrar com `aws-domain` para Amazon Transcribe (STT + diarization)
- [x] Integrar com `aws-domain` para Amazon Comprehend (sentimento + NER)
- [x] Implementar detecção de keywords de risco
- [x] Implementar IGA scorer de áudio
- [x] Configurar rastreamento Git LFS (Large File Storage) para modelos de IA (.pt) e mídias de teste (.mp4)

---

### 👨‍💻 Evandro Rosa Sampaio (Dev 3) — Document AI & Risk Domain

**Foco:** `document-domain/` + `risk-domain/`

#### Tarefas

**Document Domain:**
- [x] Configurar serviço FastAPI de documentos
- [x] Integrar com `aws-domain` para Amazon Textract (OCR)
- [x] Implementar extrator de campos obstétricos
- [x] Implementar verificador de consistência e validador de consentimento
- [x] Implementar IGA scorer documental

**Risk Domain:**
- [x] Configurar serviço FastAPI de risco
- [x] Implementar motor de correlação multimodal e calculadora do IGA
- [x] Implementar analisador de tendências temporais e gerar justificativas

---

### 👩‍💻 Gustavo Octaviano (Dev 4) — Frontend & Reports

**Foco:** `frontend/` + `report-domain/`

#### Tarefas

**Dashboard (Streamlit):**
- [x] Configurar aplicação Streamlit multipage (Dashboard, Login, Sessões)
- [x] Implementar mapa de calor temporal do IGA e sincronização
- [x] Implementar central de alertas

**Report Domain:**
- [x] Configurar serviço FastAPI de relatórios
- [x] Implementar gerador de PDF e Excel
- [x] Implementar gerador de relatório de auditoria e logs imutáveis

---

### ☁️ Wallace Gomes (Dev 5) — AWS, Security & Observability

**Foco:** `aws-domain/`, `security-domain/`, `infrastructure/` e estratégia de ambientes.

#### Responsabilidades
- Integração de serviços gerenciados de Inteligência Artificial e Storage na AWS.
- Gestão de IAM, Segurança, Anonimização e LGPD.
- Configuração e deploy dos ambientes HML e PRD.
- Observabilidade, monitoramento e gestão de segredos.

#### Backlog Completo (Sprints AWS)
- [x] **AWS Foundation**: Criação da conta AWS, configuração da VPC, Subnets e Security Groups.
- [x] **IAM**: Configuração de roles, policies e least-privilege access para ECS e desenvolvedores.
- [x] **Secrets Manager**: Migração de `.env` sensíveis para AWS Secrets Manager (Desativado no MVP/Local).
- [x] **S3 Storage**: Configuração de buckets para mídias e relatórios, com S3 Encryption (KMS) e pre-signed URLs.
- [x] **Amazon Transcribe**: Implementação do módulo de transcrição e diarização de áudio (`aws-domain`). *(Mockado para desenvolvimento local via `MOCK_AWS=True`)*
- [x] **Amazon Comprehend**: Implementação de extração de sentimento, entidades e detecção de PII (`aws-domain`). *(Mockado para desenvolvimento local via `MOCK_AWS=True`)*
- [x] **Amazon Textract**: Implementação do módulo OCR para prontuários e documentos manuscritos (`aws-domain`). *(Mockado para desenvolvimento local via `MOCK_AWS=True`)*
- [x] **CloudWatch & Observability**: Configurar envio centralizado de logs (JSON structlog) e criação de dashboards de auditoria (LGPD). *(Structlog JSON configurado. Agente pendente)*
- [x] **Security & Anonimização**: Implementar serviço de pseudo-anonimização/mascaramento de dados e encriptação AES-256 no `security-domain`.
- [x] **Deploy HML/PRD**: Criar scripts IaC (Terraform/CloudFormation) para implantação no Amazon ECS Fargate e Amazon RDS PostgreSQL. *(Base de infraestrutura VPC, ECS, RDS criada)*

---

## 2. Estratégia Git e Branching

### Modelo: Trunk-Based Development

Adotamos **trunk-based development** com feature branches de curta duração (máximo 2 dias antes do merge).

### Branches
- `main` (branch principal)
- `feat/<domínio>/<descricao>`
- `fix/<domínio>/<descricao>`
- `chore/<descricao>`
- `docs/<descricao>`

### Pull Requests
- Template obrigatório
- Mínimo **1 reviewer**
- Testes e CI (Actions) devem passar

---

## 3. Agentes de IA Especializados

### 🎯 Agent 1 — Product Owner Agent
**Objetivo:** Gerenciar e detalhar requisitos, histórias de usuário e critérios de aceite com foco em conformidade LGPD.

### 🏗️ Agent 2 — Software Architect Agent
**Objetivo:** Revisar decisões arquiteturais. Foco em arquitetura de 4 ambientes (LOCAL, DEV, HML, PRD) e integração AWS.

### ⚙️ Agent 3 — Backend Agent
**Objetivo:** Gerar código FastAPI, schemas Pydantic v2 e testes unitários.

### 🎥 Agent 4 — Video AI Agent
**Objetivo:** Especialista em visão computacional local (OpenCV, YOLOv8, MediaPipe, DeepFace) para ambiente obstétrico.

### 🎙️ Agent 5 — Audio AI Agent
**Objetivo:** Especialista em integração com Amazon Transcribe e Amazon Comprehend para processamento clínico.

### 📄 Agent 6 — Document AI Agent
**Objetivo:** Especialista em extração documental médica utilizando Amazon Textract.

### 📊 Agent 7 — Risk Correlation Agent
**Objetivo:** Calcular o IGA composto (0-100) utilizando regras de ponderação.

### 🚀 Agent 8 — DevOps Agent
**Objetivo:** Especialista em infraestrutura, CI/CD (GitHub Actions), Docker Compose (para LOCAL/DEV) e Amazon ECS Fargate (para HML/PRD).

### 🧪 Agent 9 — QA Agent
**Objetivo:** Garantir qualidade, testes e validação com pytest.

### 📝 Agent 10 — Documentation Agent
**Objetivo:** Manter documentação técnica atualizada (Markdown + Mermaid).

### ☁️ Agent 11 — AWS Integration Agent

**Nome:** GuardIA AWS Agent  
**Objetivo:** Especialista na integração segura com o ecossistema Amazon Web Services.

**Prompt Completo:**
```
Você é um Cloud Solutions Architect com foco em AWS.

CONTEXTO: Integração do GuardIA Parto Seguro com Amazon Transcribe, Amazon Comprehend, Amazon Textract e Amazon S3.

REGRAS OBRIGATÓRIAS:
- Centralizar o acesso a chaves e segredos exclusivamente no AWS Secrets Manager.
- Configurar IAM Roles e Policies baseadas em least privilege.
- Prover integrações com o SDK boto3 assíncrono (aiobotocore) para o FastAPI.
- Configurar métricas e logs estruturados no Amazon CloudWatch.

ENTRADAS: Serviço que precisa ser integrado à AWS
SAÍDAS: Módulo Python assíncrono para o AWS Integration Domain usando boto3, e scripts IaC (Terraform)
```

### 🛡️ Agent 12 — Security & LGPD Agent

**Nome:** GuardIA Security Agent  
**Objetivo:** Garantir Zero Trust, Criptografia, IAM e Conformidade LGPD.

**Prompt Completo:**
```
Você é um CISO e DPO.

CONTEXTO: Garantir anonimização e segurança no Security Domain do GuardIA.

REGRAS OBRIGATÓRIAS:
- Ocultar dados pessoais na base.
- Impor validações estritas de IAM e RBAC.
- Manter o Log de Auditoria irrefutável enviando ao CloudWatch Logs.
- S3 Encryption obrigatório.

ENTRADAS: Desenho de arquitetura ou fluxo de dados
SAÍDAS: Regras de anonimização e políticas de segurança
```
