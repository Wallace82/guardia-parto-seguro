# Backend (Core Platform) & API Specifications

O backend (orquestrador principal) do GuardIA Parto Seguro foi desenvolvido utilizando **Python + FastAPI**, devido à alta performance para operações assíncronas (asyncio) e fácil geração de documentação OpenAPI (Swagger).

## 1. Estrutura do Backend (`core-api`)

Localizado em `backend/app/`, a arquitetura interna segue o padrão de módulos (routers):

- **`/auth/`**: Gerenciamento de tokens JWT (Login, Roles - RBAC).
- **`/sessions/`**: CRUD das sessões (atendimentos médicos). Orquestra os uploads de mídia e despacha eventos assíncronos via `BackgroundTasks` para análise (Vídeo, Áudio, Documentos).
- **`/alerts/`**: Consulta e baixa (dismiss) de alertas críticos gerados pelos motores de IA em tempo real.
- **`/audit/`**: Trilha de auditoria das ações dos usuários.
- **`/orchestrator/`**: Serviço interno (Domain Client) que faz o `Fan-Out` / `Fan-In` realizando requisições HTTP para os domínios especializados (`video-service`, `risk-service`, etc) e consolidando os resultados.

## 2. Padrões Técnicos Adotados

1. **Validação e DTOs:** 100% gerenciado via `Pydantic` v2 (`schemas.py`).
2. **Banco de Dados:** PostgreSQL (Assíncrono via `SQLAlchemy` + `asyncpg`).
3. **Migrações:** Gerenciadas localmente via `Alembic` (pasta `migrations/`).
4. **Logs e Telemetria:** Adoção rigorosa do `structlog` (Logs em formato JSON) via Middleware central, padronizando atributos contextuais (`session_id`, `media_id`, `user_id`).
5. **Autenticação:** JWT Bearer tokens na rota `/api/v1/auth/login`.

## 3. Principais Endpoints da API REST

A API do `core-api` é exposta na porta `8000`.

### Autenticação
- `POST /api/v1/auth/login`: Recebe JSON com `username` (ou matricula) e `password`. Retorna `access_token` JWT.

### Sessões (Pacientes / Atendimentos)
- `POST /api/v1/sessions/`: Cria uma sessão vinculada a um paciente.
- `GET /api/v1/sessions/`: Lista sessões com paginação (limitadas pela role do usuário).
- `GET /api/v1/sessions/{id}`: Detalhes completos.
- `POST /api/v1/sessions/{id}/media`: Aceita `multipart/form-data`. O arquivo é salvo localmente no volume e dispara processamento em background (vídeo, áudio, ou documento).
- `GET /api/v1/sessions/{id}/analysis`: Ponto central para o frontend. Chama os domínios de IA internamente e compila Transcrições, Fatores Positivos e de Atenção, e Recomendações em um único JSON estruturado.
- `GET /api/v1/sessions/{id}/report/pdf`: Gera on-the-fly um PDF de Resumo Executivo da sessão utilizando FPDF.

### Alertas
- `GET /api/v1/alerts`: Lista alertas de Risco (Ex: "Risco alto identificado").
- `POST /api/v1/alerts/{id}/dismiss`: Silencia/Marca como lido.

## 4. Swagger UI (OpenAPI)

Por adotar o FastAPI, a especificação OpenAPI (Swagger) completa (com schemas, exemplos e botões "Try it out") é gerada automaticamente.

Para visualizar todos os detalhes de input/output:
1. Suba os containers (`docker-compose up -d`).
2. Acesse: **[http://localhost:8000/docs](http://localhost:8000/docs)**
3. Para acesso em formato JSON raw: **[http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)**

*Nota: Em produção, o acesso ao Swagger deve ser restrito ou desativado via configuração de ambiente.*
