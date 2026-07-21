# GuardIA Parto Seguro

O **GuardIA Parto Seguro** é uma plataforma inovadora de telemetria clínica e análise multimodal focada em vigilância obstétrica. Ele une Visão Computacional, Processamento de Linguagem Natural (NLP) e IA Generativa para auxiliar equipes de saúde a garantir um ambiente seguro, acolhedor e em conformidade com as diretrizes de humanização do parto.

> **MISSÃO**: Erradicar a violência obstétrica invisível (desrespeito verbal, não-consenso, negligência da dor) através de análise ubíqua de IA e geração de um índice dinâmico e global: o IGA (Índice GuardIA de Atenção).

---

## 🏗 Arquitetura Global

O projeto foi migrado para uma robusta infraestrutura de **Microsserviços em Monorepo**. A comunicação é gerenciada pelo núcleo `core-api`, que atua como orquestrador distribuindo tarefas para instâncias especializadas:

- **Frontend (`guardia-frontend`)**: SPA construída em Angular + Signals + Tailwind CSS.
- **Backend Core (`backend`)**: Gateway FastAPI que orquestra e persiste os dados em PostgreSQL.
- **Domínios de IA**: Serviços Python isolados e dedicados.

### 📚 Documentação Oficial

Para um entendimento profundo do sistema auditado, consulte a nossa nova central de documentação em `docs/`:

1. [Arquitetura e Fluxo (High-Level)](docs/architecture/ARCHITECTURE.md)
2. [Modelos de IA (OpenCV, MediaPipe, OpenAI)](docs/ai/AI_MODELS.md)
3. [Especificação de Backend e API](docs/backend/README.md)
4. [Dicionário de Banco de Dados (DER)](docs/database/DATABASE.md)
5. [Frontend Angular](docs/frontend/README.md)
6. [Decisões Arquiteturais (ADRs)](docs/decisions/ADR.md)
7. [Dívida Técnica e Débitos (Technical Debt)](docs/decisions/TECHNICAL_DEBT.md)
8. [Roadmap (Curto a Longo Prazo)](docs/roadmap/ROADMAP.md)
9. [Relatório Técnico (Avaliação Pós-Graduação)](docs/relatorio_tecnico.md)

---

## 🛠 Tecnologias Principais

- **Backend / Workers**: Python 3.12, FastAPI, SQLAlchemy (asyncpg), Alembic, Pydantic.
- **Frontend**: Angular 17+ (Standalone), TypeScript, Tailwind CSS, Angular Material.
- **Inteligência Artificial**: OpenCV, DeepFace, MediaPipe, SpeechRecognition (Google), OpenAI GPT-4o-mini, AWS Textract (Wrapper).
- **Persistência**: PostgreSQL 16 (Dados Clínicos) e Redis 7 (Filas/Cache).
- **Infraestrutura**: Docker e Docker Compose, FFmpeg.

---

## 🚀 Guia Completo de Instalação e Execução (Ambiente de Desenvolvimento)

Para rodar o GuardIA Parto Seguro localmente e contribuir com o projeto, siga o passo a passo abaixo.

### 1. Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas na sua máquina:
- **Git**: Para clonar o repositório.
- **Docker e Docker Compose**: Essencial para rodar o banco de dados (PostgreSQL) e os microsserviços em contêineres.
- **Node.js 18+**: Para o desenvolvimento do Frontend.
- **Angular CLI**: Instalado globalmente (`npm install -g @angular/cli`).
- **Python 3.12+**: Caso decida rodar o orquestrador ou os workers de IA nativamente fora do Docker.
- **FFmpeg**: Necessário na máquina host se rodar o `video-service` localmente sem Docker (para processamento de vídeo).

### 2. Clonando o Repositório

```bash
git clone https://github.com/seu-usuario/guardia-parto-seguro.git
cd guardia-parto-seguro
```

### 3. Configurando as Variáveis de Ambiente (.env)

O sistema depende de chaves externas de IA e configurações de banco de dados. Na raiz do projeto, crie um arquivo `.env` baseado no arquivo de exemplo:

```bash
cp .env.example .env
```

**Principais Variáveis Necessárias no `.env`:**
- `DATABASE_URL`: String de conexão com o PostgreSQL (ex: `postgresql+asyncpg://postgres:postgres@localhost:5432/core_db`).
- `OPENAI_API_KEY`: Chave da OpenAI para as funções de LLM/Generativa. **[Importante]** O sistema utiliza o modelo **GPT-4o-mini**. É um pré-requisito obrigatório que a sua chave de API tenha autorização e créditos (Tier) para acessar especificamente este modelo.
- `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`: Credenciais da AWS (necessárias para análise de documentos e áudio em nuvem).
- `AWS_REGION`: Região da AWS (ex: `us-east-1`).
- `SECRET_KEY`: Chave secreta do FastAPI para geração de tokens JWT de autenticação.

### 4. Rodando o Banco de Dados

A maneira mais fácil de subir a infraestrutura de apoio é usando o Docker Compose na raiz do projeto:

```bash
docker-compose up -d postgres-core
```
*(Isso vai liberar a porta 5432 para o banco de dados localmente).*

### 5. Rodando o Backend (Core API e Workers de IA)

Você pode optar por rodar todos os serviços via Docker ou rodar nativamente para debugar.

#### Opção A: Tudo via Docker (Recomendado para Start Rápido)
Use os scripts na raiz para subir todos os 7 microsserviços simultaneamente.
**Windows (PowerShell):**
```powershell
.\start.ps1
```
**Linux / Mac:**
```bash
chmod +x start.sh
./start.sh
```

#### Opção B: Desenvolvimento Nativo (Python)
Ideal para debugar o código do backend (`core-api`, por exemplo) ou algum worker de IA.
```bash
# Entre na pasta do backend core (ou de qualquer outro serviço)
cd backend 

# Crie e ative um ambiente virtual
python -m venv venv
# No Linux/Mac: source venv/bin/activate
# No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# (Apenas no core-api) Rode as migrações do banco de dados
alembic upgrade head

# Inicie o servidor
uvicorn app.main:app --reload --port 8000
```

### 6. Rodando o Frontend (Angular)

Para desenvolvimento de interface, recomendamos rodar o frontend fora do Docker para aproveitar o recarregamento instantâneo (*Hot Reload*).

```bash
# Abra um novo terminal e navegue para a pasta do frontend
cd guardia-frontend

# Instale as dependências do Node
npm install

# Inicie o servidor de desenvolvimento do Angular
ng serve
```

### 7. Acessando a Plataforma

Com tudo rodando, você pode acessar:
- **Painel Frontend (SPA)**: [http://localhost:4200](http://localhost:4200)
- **Documentação da API Backend (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧠 Como Funciona o IGA (Índice GuardIA de Atenção)

O sistema aceita upload (Upload File ou Camera Stream - futuro) de:
1. **Vídeo**: A IA busca picos de tensão facial e imobilidade extrema na paciente.
2. **Áudio**: A IA rastreia vocábulos de desespero/dor e afere o tom da resposta médica.
3. **Documentos**: O Textract Lê PDFs de exames; a IA identifica agravantes (como hipertensão prévia).

Os serviços reportam o risco (0 a 100) para o orquestrador (`risk-domain`), que agrupa em um score final balanceado. Acima de 70%, o painel da UTI pisca em vermelho (**Crítico**), gerando um Alerta Ativo de intervenção no banco de dados.

---

## 🤝 Contribuição e Licença
Este projeto possui fins acadêmicos e arquiteturais experimentais.
Consulte `docs/roadmap/ROADMAP.md` para priorizar issues.
Ao propor PRs, não esqueça de gerar as migrações usando `alembic revision --autogenerate`.
