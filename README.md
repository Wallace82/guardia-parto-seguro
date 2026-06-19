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

A solução utiliza uma **Arquitetura Híbrida** combinando processamento local e serviços em nuvem, processando simultaneamente **vídeos clínicos**, **áudios de consultas**, **documentos médicos** e **histórico do paciente**, gerando alertas automáticos e relatórios especializados, com rígidos controles de **Segurança e conformidade LGPD**.

---

## 🏗️ Arquitetura

```
guardia-parto-seguro/
├── infra/                   # ⚙️ Infraestrutura local (Docker, DB, scripts)
├── infrastructure/          # ☁️ Scripts e IaC (Infrastructure as Code) para Azure
├── docs/                    # 📚 Documentação completa do projeto
├── backend/                 # 🔐 Core Platform + API Gateway (FastAPI)
├── frontend/                # 🖥️ Dashboard Multimodal (Streamlit)
├── video-domain/            # 🎥 Domínio Local de Visão Computacional (OpenCV/YOLOv8/DeepFace)
├── audio-domain/            # 🎙️ Domínio de Análise de Áudio (delegado ao Azure Speech/Language)
├── document-domain/         # 📄 Domínio de Análise de Documentos (delegado ao Azure Doc Intel)
├── risk-domain/             # 📊 Domínio de Correlação de Risco (IRA)
├── report-domain/           # 📋 Domínio de Relatórios
├── cloud-domain/            # 🌩️ Cloud Integration Domain (Storage, Azure AI, Auditoria)
├── security-domain/         # 🛡️ Security Domain (LGPD, Auth, Anonimização, RBAC)
├── start.ps1                # ▶️ Script de startup (Windows)
└── start.sh                 # ▶️ Script de startup (Linux/macOS)
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
| **Wallace Gomes (Dev 1)** | Core Platform & DevOps | `backend/`, `infra/` |
| **Paulo Roberto Gonçalves (Dev 2)** | Video & Audio AI | `video-domain/`, `audio-domain/` |
| **Evandro Rosa Sampaio (Dev 3)** | Document AI & Risk | `document-domain/`, `risk-domain/` |
| **Gustavo Octaviano (Dev 4)** | Frontend & Reports | `frontend/`, `report-domain/` |

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura híbrida completa, diagramas C4, fluxos |
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | Requisitos funcionais, não funcionais, regras de negócio e segurança |
| [DOMAINS.md](docs/DOMAINS.md) | Definição completa de todos os domínios (incluindo Cloud e Security) |
| [API_SPEC.md](docs/API_SPEC.md) | Especificação OpenAPI de todas as APIs |
| [DATABASE.md](docs/DATABASE.md) | Modelo de dados, DDL e relacionamentos |
| [DEVOPS.md](docs/DEVOPS.md) | CI/CD, segurança, Docker, estratégia de deploy |
| [SECURITY.md](docs/SECURITY.md) | Diretrizes de Criptografia, RBAC, Auditoria, Gestão de Segredos e LGPD |
| [TEAM_PLAN.md](docs/TEAM_PLAN.md) | Plano da equipe, responsabilidades e agentes IA |
| [ROADMAP.md](docs/ROADMAP.md) | Roadmap de execução com Sprints de Segurança e Nuvem |
| [RISK_MATRIX.md](docs/RISK_MATRIX.md) | Matriz de riscos (incluindo custos, vazamento e LGPD) e mitigações |

---

## 🤖 Tecnologias & Mapeamento de Bibliotecas

Para garantir escalabilidade, isolamento de domínios e alta performance assíncrona, a plataforma é estruturada em microsserviços. Abaixo, detalhamos o ecossistema tecnológico distribuído nos contextos de **Arquitetura**, **Backend & IA**, **Frontend & Dados** e **Infraestrutura**, vinculando as principais bibliotecas Python aos problemas que resolvem:

### 1. 🏗️ Contexto de Arquitetura (Integração & Orquestração)
Define as tecnologias responsáveis pelo roteamento de requisições, modelagem de dados, comunicação entre microsserviços e governança do fluxo multimodal.

*   **FastAPI (`0.110.0`)**
    *   *Problema que resolve:* Necessidade de expor APIs RESTful assíncronas de baixíssima latência e documentação OpenAPI automática (Swagger) para os serviços de domínio.
    *   *Solução:* Serve como a espinha dorsal do API Gateway principal e de todos os microsserviços, permitindo alta concorrência com o paradigma `async/await`.
*   **Pydantic & Pydantic-Settings (`2.7.0` / `2.2.1`)**
    *   *Problema que resolve:* Validação em tempo de execução de dados estruturados que transitam na rede e gestão segura de configurações.
    *   *Solução:* Valida e sanitiza cargas úteis de dados (JSON) de entrada e saída, além de mapear com segurança e tipagem estrita as variáveis de ambiente (`.env`).
*   **HTTPX (`0.27.0`)**
    *   *Problema que resolve:* Bloqueio de threads em requisições HTTP entre microsserviços internos.
    *   *Solução:* Realiza requisições HTTP assíncronas de forma não bloqueante, permitindo que o API Gateway dispare análises paralelas aos domínios de Vídeo, Áudio e Documentos de forma simultânea.

### 2. 🔐 Contexto de Backend & Inteligência Artificial
Compreende o núcleo de inteligência analítica multimodal e as capacidades de segurança do sistema.

#### A. Domínio de Vídeo e Visão Computacional (`video-domain`)
*   **OpenCV (opencv-python-headless `4.9.0.80`)**
    *   *Problema que resolve:* Processamento de vídeo bruto, decodificação de frames em tempo real e manipulação geométrica de imagens.
    *   *Solução:* Trata fluxos de imagem com eficiência em containers Docker sem dependência de drivers de interface gráfica (headless).
*   **MediaPipe (`0.10.11`)**
    *   *Problema que resolve:* Análise de movimentação, estimativa de pose corporal e detecção de pontos de articulação de profissionais e gestantes.
    *   *Solução:* Mapeia coordenadas corporais e faciais tridimensionais (3D joints) para identificar padrões de queda, movimentos bruscos e posicionamentos anômalos.
*   **DeepFace (`0.0.91`)**
    *   *Problema que resolve:* Monitoramento de expressões faciais indicativas de sofrimento agudo da paciente no ambiente assistencial.
    *   *Solução:* Realiza análise de atributos faciais para detecção de emoções primárias (dor, medo, tristeza, raiva), provendo inputs quantitativos ao Índice de Risco Assistencial (IRA).
*   **Ultralytics YOLOv8 (`8.2.0`)**
    *   *Problema que resolve:* Rastreamento em tempo real de objetos clínicos no ambiente (ex. presença de maca, bed occupancy, instrumentos cirúrgicos) e eventos atípicos (ex. manchas de sangue/hemorragias).
    *   *Solução:* Detecta e classifica objetos na cena com alta precisão e baixíssimo tempo de inferência.
*   **face-recognition (`1.3.0`)**
    *   *Problema que resolve:* Identificação inequívoca de pacientes e profissionais para controle de auditoria e segurança.
    *   *Solução:* Reconhecimento facial robusto baseado em redes neurais profundas pré-treinadas.
*   **Pillow (`10.3.0`) & NumPy (`1.26.4`)**
    *   *Problema que resolve:* Manipulação genérica de dados de imagem e arrays matriciais em alta performance.

#### B. Domínio de Áudio e Linguagem Natural (`audio-domain`)
*   **azure-cognitiveservices-speech (`1.37.0`)**
    *   *Problema que resolve:* Transcrição de áudio contínuo de conversas e consultas médicas (Speech-to-Text).
    *   *Solução:* Converte voz em texto em português, com reconhecimento acústico de terminologia médica e suporte a múltiplos interlocutores.
*   **azure-ai-textanalytics (`5.3.0`)**
    *   *Problema que resolve:* Necessidade de extrair sentimentos e termos sensíveis das falas transcritas.
    *   *Solução:* Analisa o texto transcrito em busca de sentimentos negativos (medo, coação) e entidades clínicas específicas (termos indicativos de abuso verbal ou violência obstétrica).

#### C. Domínio de Documentos (`document-domain`)
*   **azure-ai-documentintelligence (`1.0.0`)**
    *   *Problema que resolve:* Extração de textos de documentos digitalizados ou manuscritos (prontuários, termos de consentimento, laudos).
    *   *Solução:* Executa OCR inteligente e mapeamento de chaves, tabelas e valores, estruturando dados antes ilegíveis para correlacionar com o histórico.

#### D. Integração Cloud & Segurança Híbrida (`cloud-domain`, `security-domain`)
*   **Azure Identity & Key Vault (`azure-identity`, `azure-keyvault-secrets`)**
    *   *Problema:* Proteção de segredos e credenciais, garantindo conformidade com arquiteturas Zero Trust.
    *   *Solução:* Busca dinamicamente senhas, conexões e chaves diretamente do Azure Key Vault. Nenhuma credencial fica em código-fonte ou `.env` de produção.
*   **Azure Monitor & Auditoria**
    *   *Problema:* Observabilidade e rastreabilidade (requisito LGPD).
    *   *Solução:* Centraliza logs estruturados de acessos, uploads e cálculos de risco em tempo real.
*   **Módulo de Anonimização & LGPD**
    *   *Problema:* Necessidade de ocultar dados sensíveis de pacientes em logs e bancos de dados (Ex: Maria Silva → PACIENTE_001).
    *   *Solução:* Módulo de criptografia AES-256 para repouso, mascaramento e hash unidirecional para identificadores, operando no Security Domain.
*   **python-jose (`3.3.0`) & passlib (`1.7.4`)**
    *   *Problema:* Autenticação e RBAC (Role-Based Access Control).
    *   *Solução:* Controla o acesso via JWT com validação forte para os perfis: Admin, Gestor, Médico, Enfermeiro e Auditor.

### 3. 🖥️ Contexto de Frontend & Geração de Relatórios
Garante a interface do usuário final de monitoramento e a confecção de arquivos exportáveis para ouvidorias e órgãos fiscalizadores.

*   **Streamlit (`1.35.0`)**
    *   *Problema que resolve:* Necessidade de criar e iterar rapidamente em um painel interativo sem criar uma complexa estrutura de frontend em React/HTML/CSS do zero.
    *   *Solução:* Renderiza o painel principal, gráficos de risco (IRA) e tocadores de mídia a partir de scripts simples em Python.
*   **Plotly (`5.21.0`)**
    *   *Problema que resolve:* Apresentação estática e pouco intuitiva de métricas e tendências temporais de saúde.
    *   *Solução:* Plota gráficos de linha e barras totalmente interativos com suporte a zoom e tooltips informativos.
*   **Pandas (`2.2.2`)**
    *   *Problema que resolve:* Organização de coleções complexas de dados do histórico de alertas e exames.
    *   *Solução:* Permite ordenação rápida, filtragem temporal e pivotagem de dados em estruturas de DataFrames.
*   **reportlab (`4.1.0`)**
    *   *Problema que resolve:* Geração de documentos físicos imutáveis de auditoria e prontuários consolidados.
    *   *Solução:* Constrói PDFs altamente customizados com logos, cabeçalhos dinâmicos, tabelas paginadas e metadados de assinatura.
*   **openpyxl (`3.1.2`)**
    *   *Problema que resolve:* Necessidade de exportar bases históricas de auditoria para manipulação externa por gestores hospitalares.
    *   *Solução:* Exporta planilhas em formato nativo Excel (`.xlsx`).
*   **Jinja2 (`3.1.4`)**
    *   *Problema que resolve:* Acoplamento de strings para envio de e-mails de alerta ou relatórios simples.
    *   *Solução:* Renderiza templates dinâmicos injetando dados em marcações HTML pré-existentes.

### 4. ⚙️ Contexto de Infraestrutura & Integração com Nuvem
Garante que a persistência relacional local e a conectividade com serviços de nuvem funcionem de forma assíncrona, robusta e sob a ótica de segurança Zero-Trust.

*   **SQLAlchemy (`2.0.29`) & asyncpg (`0.29.0`)**
    *   *Problema que resolve:* Bloqueio de IO em operações de banco de dados e acoplamento a SQL dialetos.
    *   *Solução:* Proveem um ORM robusto mapeado sob transações assíncronas utilizando o driver assíncrono nativo para o PostgreSQL.
*   **Alembic (`1.13.1`)**
    *   *Problema que resolve:* Dificuldade de manter consistência de schemas de tabelas entre ambientes de desenvolvimento e produção.
    *   *Solução:* Gerencia migrações incrementais do banco por meio de código Python.
*   **azure-storage-blob (`12.19.1`)**
    *   *Problema que resolve:* Custos e instabilidade física ao armazenar arquivos pesados de vídeo/áudio no disco local dos microsserviços.
    *   *Solução:* Gerencia uploads assíncronos diretamente para contêineres de blobs Azure com segurança via SAS Tokens.
*   **azure-identity (`1.16.0`)**
    *   *Problema que resolve:* Chaves de API e segredos vulneráveis no código fonte (`credentials leakage`).
    *   *Solução:* Permite autenticação sem senhas (passwordless) via Identidades Gerenciadas nos recursos Azure.
*   **azure-keyvault-secrets (`4.8.0`)**
    *   *Problema que resolve:* Distribuição centralizada de credenciais sensíveis (ex. chaves SMTP, segredos JWT) em ambiente distribuído.
    *   *Solução:* Recupera credenciais dinamicamente sob demanda.
*   **Docker & Docker Compose**
    *   *Problema que resolve:* Instabilidade de ambiente ("funciona na minha máquina").
    *   *Solução:* Isola os 9 containers em redes virtuais controladas por variáveis de ambiente.
*   **PostgreSQL 16 & Redis 7**
    *   *Problema que resolve:* Persistência de dados altamente estruturados e necessidade de cache / filas de processamento rápido.

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
