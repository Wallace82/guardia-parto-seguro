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
├── infra/                   # ⚙️  Toda a infraestrutura (Docker, DB, scripts)
│   ├── docker-compose.yml   #     Orquestração de todos os containers
│   ├── postgres/            #     Scripts de inicialização do banco
│   ├── scripts/             #     Scripts utilitários de infra
│   └── nginx/               #     Configuração de reverse proxy (futuro)
├── docs/                    # 📚 Documentação completa do projeto
├── backend/                 # 🔐 Core Platform + API Gateway (FastAPI)
├── frontend/                # 🖥️  Dashboard Multimodal (Streamlit)
├── video-domain/            # 🎥 Domínio de Análise de Vídeo
├── audio-domain/            # 🎙️  Domínio de Análise de Áudio
├── document-domain/         # 📄 Domínio de Análise de Documentos
├── risk-domain/             # 📊 Domínio de Correlação de Risco (IRA)
├── report-domain/           # 📋 Domínio de Relatórios
├── start.ps1                # ▶️  Script de startup (Windows)
└── start.sh                 # ▶️  Script de startup (Linux/macOS)
```

Veja a documentação completa em [ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🚀 Início Rápido

### Pré-requisitos

- Docker Desktop (inclui Docker Compose)
- Git
- Conta Azure (para serviços de IA — opcional em desenvolvimento)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-org/guardia-parto-seguro.git
cd guardia-parto-seguro
```

### 2. Inicie o projeto

> O script de startup configura o `.env`, aguarda os bancos ficarem saudáveis e sobe todos os containers automaticamente.

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Linux / macOS:**
```bash
chmod +x start.sh
./start.sh
```

### 3. Acesse os serviços

| Serviço | URL | Descrição |
|---|---|---|
| **Dashboard** | http://localhost:8501 | Streamlit frontend |
| **API Gateway** | http://localhost:8000 | FastAPI backend principal |
| **Swagger UI** | http://localhost:8000/docs | Documentação interativa da API |
| Video Service | http://localhost:8001 | Análise de vídeo (OpenCV/DeepFace) |
| Audio Service | http://localhost:8002 | Análise de áudio (Azure Speech) |
| Document Service | http://localhost:8003 | OCR e análise documental |
| Risk Service | http://localhost:8004 | Cálculo do IRA |
| Report Service | http://localhost:8005 | Geração de PDF/Excel |

---

## ⚙️ Comandos do Script de Startup

| Comando | Descrição |
|---|---|
| `.\start.ps1` | Sobe todos os containers (cria `.env` se não existir) |
| `.\start.ps1 -Build` | Força rebuild de todas as imagens Docker |
| `.\start.ps1 -Down` | Para e remove todos os containers |
| `.\start.ps1 -Status` | Exibe status atual dos containers |
| `.\start.ps1 -Logs` | Sobe os containers e exibe logs ao vivo |
| `.\start.ps1 -Reset` | **⚠️ Remove volumes** e reinicia do zero |

> Substitua `.\start.ps1` por `./start.sh` no Linux/macOS com as mesmas flags (`--build`, `--down`, etc.).

---

## 🗂️ Infraestrutura (`infra/`)

Toda a configuração de infraestrutura está centralizada em [`infra/`](infra/):

| Arquivo | Descrição |
|---|---|
| [`infra/docker-compose.yml`](infra/docker-compose.yml) | Orquestração de 9 containers (2 PostgreSQL, Redis, 6 serviços + frontend) |
| [`infra/postgres/init-domains.sql`](infra/postgres/init-domains.sql) | Inicializa os 5 bancos de domínio na primeira execução |
| [`infra/scripts/`](infra/scripts/) | Scripts utilitários (backup, migração, seed) |

Para executar comandos Docker manualmente:

```bash
# Rodar diretamente com o compose
docker compose -f infra/docker-compose.yml up -d

# Ver logs de um serviço específico
docker compose -f infra/docker-compose.yml logs -f core-api

# Acessar o banco core_db
docker exec -it guardia-postgres-core psql -U guardia -d core_db
```

---

## 👥 Equipe de Desenvolvimento

| Dev | Papel | Domínios |
|---|---|---|
| **Dev 1** | Core Platform & DevOps | `backend/`, `infra/` |
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

### Infraestrutura
- **Docker + Docker Compose** — Containerização (`infra/`)
- **PostgreSQL 16** — 2 instâncias: `core_db` + bancos de domínio
- **Redis 7** — Cache e filas de sessão
- **Azure Blob Storage** — Armazenamento de mídias
- **Azure Key Vault** — Gerenciamento de segredos
- **Azure Monitor** — Observabilidade e alertas

### Frontend & Dados
- **Streamlit** — Dashboard interativo
- **SQLAlchemy 2.0 + Alembic** — ORM assíncrono e migrations

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
