# 🛡️ GuardIA Parto Seguro

> **Plataforma Multimodal de Inteligência Artificial para Vigilância Obstétrica e Proteção Materno-Infantil**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4?logo=microsoft-azure)](https://azure.microsoft.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Visão Geral

O **GuardIA Parto Seguro** é uma plataforma acadêmica de inteligência artificial multimodal projetada para detectar e alertar sobre situações de risco no ambiente obstétrico, incluindo:

- 🚨 Violência obstétrica
- 😰 Sofrimento psicológico e ansiedade gestacional
- 💔 Depressão pós-parto
- 🏠 Indicadores de violência doméstica
- 🩸 Sangramento anômalo
- ⚠️ Desvios em procedimentos obstétricos
- 📊 Indicadores de Risco Assistencial (IRA)

A solução processa simultaneamente **vídeos clínicos**, **áudios de consultas**, **documentos médicos** e **histórico do paciente**, gerando alertas automáticos e relatórios especializados.

---

## 🏗️ Arquitetura

```
guardia-parto-seguro/
├── docs/                    # Documentação completa do projeto
├── backend/                 # Core Platform + API Gateway (FastAPI)
├── frontend/                # Dashboard Multimodal (Streamlit)
├── video-domain/            # Domínio de Análise de Vídeo
├── audio-domain/            # Domínio de Análise de Áudio
├── document-domain/         # Domínio de Análise de Documentos
├── risk-domain/             # Domínio de Correlação de Risco (IRA)
├── report-domain/           # Domínio de Relatórios
└── devops/                  # CI/CD, Docker, Infraestrutura
```

Veja a documentação completa em [ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16+
- Conta Azure (com os serviços habilitados)
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/seu-org/guardia-parto-seguro.git
cd guardia-parto-seguro
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas credenciais Azure e PostgreSQL
```

### 3. Suba os serviços com Docker Compose

```bash
docker-compose -f devops/docker-compose.yml up -d
```

### 4. Acesse os serviços

| Serviço | URL | Descrição |
|---|---|---|
| API Gateway | http://localhost:8000 | FastAPI backend principal |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Dashboard | http://localhost:8501 | Streamlit frontend |
| Video API | http://localhost:8001 | Serviço de análise de vídeo |
| Audio API | http://localhost:8002 | Serviço de análise de áudio |
| Document API | http://localhost:8003 | Serviço de análise documental |
| Risk API | http://localhost:8004 | Cálculo do IRA |
| Report API | http://localhost:8005 | Geração de relatórios |

---

## 👥 Equipe de Desenvolvimento

| Dev | Papel | Domínios |
|---|---|---|
| **Dev 1** | Core Platform & DevOps | `backend/`, `devops/` |
| **Dev 2** | Video & Audio AI | `video-domain/`, `audio-domain/` |
| **Dev 3** | Document AI & Risk | `document-domain/`, `risk-domain/` |
| **Dev 4** | Frontend & Reports | `frontend/`, `report-domain/` |

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura completa, diagramas C4, fluxos |
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | Requisitos funcionais, não funcionais e regras de negócio |
| [DOMAINS.md](docs/DOMAINS.md) | Definição completa de todos os domínios |
| [API_SPEC.md](docs/API_SPEC.md) | Especificação OpenAPI de todas as APIs |
| [DATABASE.md](docs/DATABASE.md) | Modelo de dados, DDL e relacionamentos |
| [DEVOPS.md](docs/DEVOPS.md) | CI/CD, Docker, estratégia de deploy |
| [TEAM_PLAN.md](docs/TEAM_PLAN.md) | Plano da equipe, responsabilidades e agentes IA |
| [ROADMAP.md](docs/ROADMAP.md) | Roadmap de 8 semanas com critérios de aceite |
| [RISKS.md](docs/RISKS.md) | Matriz de riscos e mitigações |

---

## 🤖 Tecnologias

### Backend & IA
- **FastAPI** — API Gateway principal
- **OpenCV + MediaPipe + DeepFace + YOLOv8** — Visão computacional
- **Azure Speech + Azure AI Language** — Processamento de áudio e linguagem
- **Azure Document Intelligence** — Análise de documentos

### Infraestrutura Azure
- **Azure Blob Storage** — Armazenamento de mídias
- **Azure Key Vault** — Gerenciamento de segredos
- **Azure Monitor** — Observabilidade e alertas

### Frontend & Dados
- **Streamlit** — Dashboard interativo
- **PostgreSQL 16** — Banco de dados relacional
- **Docker** — Containerização

---

## 📋 Contribuindo

Leia o [TEAM_PLAN.md](docs/TEAM_PLAN.md) para entender a estratégia Git, branches e processo de code review.

**Branch principal:** `main` (trunk-based development)  
**Branches de feature:** `feat/<domínio>/<descricao>`  
**Releases:** Tags semânticas `v1.0.0`

---

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos — FIAP Tech Challenge.

---

*Desenvolvido com 💙 para proteção materno-infantil.*
