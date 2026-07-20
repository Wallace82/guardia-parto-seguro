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

---

## 🛠 Tecnologias Principais

- **Backend / Workers**: Python 3.12, FastAPI, SQLAlchemy (asyncpg), Alembic, Pydantic.
- **Frontend**: Angular 17+ (Standalone), TypeScript, Tailwind CSS, Angular Material.
- **Inteligência Artificial**: OpenCV, DeepFace, MediaPipe, SpeechRecognition (Google), OpenAI GPT-4o-mini, AWS Textract (Wrapper).
- **Persistência**: PostgreSQL 16 (Dados Clínicos) e Redis 7 (Filas/Cache).
- **Infraestrutura**: Docker e Docker Compose, FFmpeg.

---

## 🚀 Instalação e Execução (Ambiente de Desenvolvimento)

### Pré-requisitos
- **Docker** e **Docker Compose**
- Python 3.12+ (caso rode algum serviço nativamente)
- Node.js 18+ e Angular CLI
- Variáveis de ambiente configuradas no arquivo `.env` (Copie de `.env.example` e certifique-se de preencher `OPENAI_API_KEY`).

### Start Rápido (Docker)

Todo o orquestramento de Containers está centralizado nos scripts de start da raiz:

**Windows (PowerShell)**:
```powershell
.\start.ps1
```

**Linux / Mac**:
```bash
chmod +x start.sh
./start.sh
```

Isso subirá:
1. Banco de Dados e Redis.
2. Todas as 7 APIs de microsserviços.
3. O Frontend (na porta do seu localhost configurado ou requerendo `ng serve`).

*Para rodar o frontend localmente fora do docker (recomendado para desenvolvimento)*:
```bash
cd guardia-frontend
npm install
ng serve
```

Acesse em: `http://localhost:4200`

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
