# 🛡️ GuardIA Parto Seguro

> **Plataforma Multimodal de Inteligência Artificial para Vigilância Obstétrica e Proteção Materno-Infantil**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Angular 18+](https://img.shields.io/badge/Angular 18+-1.35+-FF4B4B?logo=Angular 18+)](https://Angular 18+.io/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-232F3E?logo=amazon-aws)](https://aws.amazon.com/)
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
- 📊 Indicadores de Risco Assistencial (IGA)

A solução utiliza uma **Arquitetura Híbrida** (MVP Local + AWS), processando simultaneamente **vídeos clínicos**, **áudios de consultas**, **documentos médicos** e **histórico do paciente**. As aplicações e bancos rodam localmente, enquanto os serviços cognitivos e de IA avançada são delegados via API à AWS, gerando alertas automáticos e relatórios especializados, com rígidos controles de **Segurança e conformidade LGPD**.

---

## 🏗️ Arquitetura e Ambientes

A estratégia arquitetural está dividida em quatro ambientes ([Detalhes em ENVIRONMENTS.md](docs/ENVIRONMENTS.md)):
* **LOCAL/DEV**: Execução local (MVP) consumindo APIs da AWS (Transcribe, Comprehend, Textract, S3).
* **HML/PRD**: Implantação 100% nuvem AWS (ECS, RDS, S3, Secrets Manager, CloudWatch).

```
guardia-parto-seguro/
├── infra/                   # ⚙️ Infraestrutura local (Docker, DB, scripts)
├── infrastructure/          # ☁️ Scripts e IaC (Infrastructure as Code) para AWS
├── docs/                    # 📚 Documentação completa do projeto
├── backend/                 # 🔐 Core Platform + API Gateway (FastAPI)
├── frontend/                # 🖥️ Dashboard Multimodal (Angular 18+)
├── video-domain/            # 🎥 Domínio Local de Visão Computacional (OpenCV/YOLOv8/DeepFace)
├── audio-domain/            # 🎙️ Domínio de Análise de Áudio (delegado ao Amazon Transcribe/Comprehend)
├── document-domain/         # 📄 Domínio de Análise de Documentos (delegado ao Amazon Textract)
├── risk-domain/             # 📊 Domínio de Correlação de Risco (IGA)
├── report-domain/           # 📋 Domínio de Relatórios
├── aws-domain/              # 🌩️ AWS Integration Domain (S3, AWS AI, Secrets Manager, CloudWatch)
├── security-domain/         # 🛡️ Security Domain (LGPD, IAM, Anonimização, Crypto)
├── environments/            # 🌍 Configurações e docker-composes específicos de ambientes
├── start.ps1                # ▶️ Script de startup (Windows)
└── start.sh                 # ▶️ Script de startup (Linux/macOS)
```

Veja a documentação completa em [ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🚀 Início Rápido

Siga os passos abaixo para preparar e executar o projeto na sua máquina pela primeira vez.

### Pré-requisitos

- Docker Desktop (inclui Docker Compose)
- Git
- Python 3.11+ instalado
- Conta AWS (Free Tier) com Usuário IAM criado contendo `AdministratorAccess` (ou acesso full a S3, Textract e Transcribe)
- Access Key e Secret Access Key geradas no IAM.

### 1. Clone o repositório

```bash
git clone https://github.com/Wallace82/guardia-parto-seguro.git
cd guardia-parto-seguro
```

### 2. Configuração de Variáveis de Ambiente (.env)

O projeto requer credenciais da AWS para funcionar (armazenamento e IA).

1. Crie uma cópia do arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```
2. Abra o arquivo `.env` gerado.
3. Localize o bloco `============ AWS CONFIGURATION ============` e preencha com as chaves que você gerou no console da AWS:
   ```env
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=Uhf...
   AWS_REGION=us-east-1
   ```

### 3. Provisionamento da Infraestrutura AWS (S3)

Nós utilizamos buckets S3 reais para armazenar mídias e relatórios. Execute o script Python para criá-los automaticamente na sua conta AWS:

```bash
# Crie um ambiente virtual (recomendado) e instale o boto3
pip install boto3 python-dotenv

# Rode o script de provisionamento
python setup_buckets.py
```
> Se der sucesso, o terminal informará que os buckets foram criados e o seu `.env` será preenchido com os nomes corretos dos buckets (`MEDIA_BUCKET_NAME` e `REPORTS_BUCKET_NAME`).

### 4. Inicie o projeto

O script de startup faz o build das imagens Docker, sobe os bancos de dados (PostgreSQL/Redis) e todos os microsserviços do ambiente LOCAL.

**Windows (PowerShell):**
```powershell
.\start.ps1 -Build
```

**Linux / macOS:**
```bash
chmod +x start.sh
./start.sh --build
```

### 5. Inicie o Frontend (Angular)

Como o frontend Angular não roda no Docker localmente para facilitar o desenvolvimento, você precisa iniciá-lo separadamente:

```bash
cd guardia-frontend
npm install
npm start # ou ng serve
```

### 6. Acesse e Teste os Serviços

| Serviço | URL | Descrição |
|---|---|---|
| **Dashboard (Angular)** | http://localhost:4200 | Interface Frontend principal |
| **API Gateway** | http://localhost:8000 | FastAPI backend principal |
| **AWS Domain** | http://localhost:8007 | IA da AWS (S3, Textract, etc) |
| **Swagger UI** | http://localhost:8007/docs | Documentação interativa da API AWS |

#### 🧪 Testando a Inteligência Artificial na Prática (Dashboard & Postman)

O fluxo completo de upload e análise multimodal pode ser operado de forma simples e visual diretamente pelo **Dashboard Angular 18+**. Caso prefira testar os endpoints de integração individualmente, disponibilizamos nossa Collection do Postman:
1. Abra o Postman.
2. Importe o arquivo na raiz do projeto: `docs/postman/GuardIA_AWS_Domain.postman_collection.json`.
3. Siga o passo a passo das requisições na ordem (Gerar URL -> Fazer Upload do PDF -> Analisar no Textract -> Obter Resultados).

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
| **Wallace Gomes (Dev 1)** | Core Platform & DevOps | `backend/`, `infra/` |
| **Paulo Roberto Gonçalves (Dev 2)** | Video & Audio AI | `video-domain/`, `audio-domain/` |
| **Evandro Rosa Sampaio (Dev 3)** | Document AI & Risk | `document-domain/`, `risk-domain/` |
| **Gustavo Octaviano (Dev 4)** | Frontend & Reports | `frontend/`, `report-domain/` |
| **Wallace Gomes (Dev 5)** | Nuvem AWS, Segurança, Observabilidade | `aws-domain/`, `security-domain/`, `infrastructure/` |

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura híbrida completa, diagramas C4, fluxos |
| [ENVIRONMENTS.md](docs/ENVIRONMENTS.md) | Estratégia de 4 ambientes (LOCAL, DEV, HML, PRD) |
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | Requisitos funcionais, não funcionais, regras de negócio e segurança |
| [DOMAINS.md](docs/DOMAINS.md) | Definição completa de todos os domínios (incluindo AWS e Security) |
| [API_SPEC.md](docs/API_SPEC.md) | Especificação OpenAPI de todas as APIs |
| [DATABASE.md](docs/DATABASE.md) | Modelo de dados, DDL e relacionamentos |
| [DEVOPS.md](docs/DEVOPS.md) | CI/CD, segurança, Docker, estratégia de deploy |
| [SECURITY.md](docs/SECURITY.md) | Criptografia, RBAC, CloudWatch, Gestão de Segredos via AWS Secrets Manager e LGPD |
| [TEAM_PLAN.md](docs/TEAM_PLAN.md) | Plano da equipe, responsabilidades e backlog Cloud |
| [ROADMAP.md](docs/ROADMAP.md) | Roadmap de execução com Sprints de Nuvem AWS, Segurança e Observabilidade |
| [RISK_MATRIX.md](docs/RISK_MATRIX.md) | Matriz de riscos e mitigações (LGPD, IAM, AWS) |

---

## 🤖 Tecnologias & Mapeamento de Bibliotecas

Para garantir escalabilidade, isolamento de domínios e alta performance assíncrona, a plataforma é estruturada em microsserviços. Abaixo, detalhamos o ecossistema tecnológico.

### 1. 🏗️ Contexto de Arquitetura (Integração & Orquestração)
*   **FastAPI** e **Pydantic**: APIs assíncronas, validação de dados e OpenAPI.
*   **HTTPX**: Requisições HTTP não bloqueantes entre microsserviços.

### 2. 🔐 Contexto de Backend & Inteligência Artificial

#### A. Domínio de Vídeo e Visão Computacional (`video-domain`)
*   **OpenCV**, **MediaPipe**, **DeepFace**, **Ultralytics YOLOv8**, **face-recognition**. Modelos rodando localmente para análise inferencial de pose, reconhecimento e expressões.

#### B. Domínio de Áudio e Linguagem Natural (`audio-domain`)
*   **Amazon Transcribe (boto3)**: Transcrição de áudio contínuo de conversas e consultas médicas (Speech-to-Text).
*   **Amazon Comprehend (boto3)**: Extração de sentimentos, PII e entidades clínicas de falas transcritas.

#### C. Domínio de Documentos (`document-domain`)
*   **Amazon Textract (boto3)**: OCR inteligente para extração de textos de documentos digitalizados ou manuscritos estruturando dados.

#### D. AWS Integration Domain & Segurança Híbrida (`aws-domain`, `security-domain`)
*   **AWS Secrets Manager (boto3)**: Proteção de segredos e credenciais, garantindo conformidade com arquiteturas Zero Trust.
*   **Amazon CloudWatch**: Centraliza logs estruturados de acessos, uploads e cálculos de risco em tempo real para auditoria.
*   **AWS IAM**: Políticas rígidas de controle de acesso para serviços e identidades de execução.
*   **Módulo de Anonimização & LGPD**: Criptografia AES-256 (S3 Encryption), mascaramento e hash unidirecional para identificadores sensíveis.

### 3. 🖥️ Contexto de Frontend & Geração de Relatórios
*   **Angular 18+**, **Plotly**, **Pandas**: Criação de dashboard, gráficos de risco e análise iterativa.
*   **reportlab**, **openpyxl**, **Jinja2**: Geração de PDFs (auditoria) e planilhas, com relatórios dinâmicos.

### 4. ⚙️ Contexto de Infraestrutura & Integração com Nuvem
*   **SQLAlchemy** & **asyncpg**: ORM assíncrono conectado ao PostgreSQL local.
*   **Amazon S3 (boto3)**: Armazenamento em nuvem para arquivos pesados de vídeo/áudio e logs protegidos.
*   **Docker & Docker Compose**: Orquestração local dos containers para MVP.
*   **PostgreSQL 16 & Redis 7**: Bancos em containers para LOCAL/DEV. Instâncias em Amazon RDS para HML/PRD.

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
