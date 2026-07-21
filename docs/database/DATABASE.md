# Banco de Dados (GuardIA Parto Seguro)

O projeto utiliza **PostgreSQL 16** como banco de dados transacional e **Redis 7** para *caching* e intermediação de filas assíncronas. O ORM escolhido é o **SQLAlchemy 2.0 (asyncpg)** com o controle de versionamento de esquema feito pelo **Alembic**.

## 1. Migrações e Inicialização

O esquema de banco NÃO é gerado com `metadata.create_all()`. Todo o versionamento está restrito às migrações do Alembic localizadas em `backend/migrations/versions`.
O banco inicial é semeado (seeded) com dados mockados (Admin, Usuários de Teste) através do script `backend/seed.py`.

## 2. Dicionário de Dados (Entidades Principais)

### 2.1 Tabela `users`
Armazena a identidade dos profissionais que utilizam o sistema.
- **id** (INT PK)
- **username** (VARCHAR) - Pode ser o nome ou matrícula (ex: CRM, COREN).
- **hashed_password** (VARCHAR)
- **role** (VARCHAR) - `admin`, `gestor`, `profissional`, `auditor`.
- **is_active** (BOOLEAN)

### 2.2 Tabela `sessions`
Centraliza um atendimento / parto monitorado.
- **id** (INT PK)
- **title** (VARCHAR) - Título ou breve descrição da sessão.
- **patient_code** (VARCHAR) - Código anonimizado da paciente, essencial para LGPD.
- **professional_id** (FK users.id) - Médico/enfermeiro responsável pela sessão.
- **status** (ENUM) - `pending`, `processing`, `completed`, `error`.
- **notes** (TEXT) - Anotações clínicas inseridas manualmente.
- **iga_score** (FLOAT) - Índice global (Índice GuardIA de Atenção).
- **iga_level** (VARCHAR) - `baixo`, `moderado`, `critico`.

### 2.3 Tabela `media_files`
Armazena as referências físicas dos arquivos atrelados à sessão. O arquivo binário real reside no Docker Volume `/shared_media`.
- **id** (INT PK)
- **session_id** (FK sessions.id)
- **media_type** (ENUM) - `video`, `audio`, `document`.
- **filename** (VARCHAR)
- **blob_url** (VARCHAR) - Caminho local (ex: `/shared_media/video.mp4`).
- **status** (ENUM) - `uploaded`, `processing`, `analyzed`, `error`.

### 2.4 Tabelas de Análise Analítica (O Motor Multimodal)
Novas entidades criadas para granularidade nas análises baseadas em evidências:
- **`video_analysis`**: Registra `key_findings`, quantidade total e analisada de frames, e pontuação postural/emocional isolada.
- **`audio_analysis`**: Registra `transcription` bruta, achados de sentimentos extraídos via IA semântica, e `duration_seconds`.
- **`document_analysis`**: Registra textos brutos do OCR, e JSONs gerados pela extração inteligente, suportando também a análise text-based das *anotações*.

### 2.5 Tabela `alerts`
Armazena alertas críticos que devem ser notificados ao corpo clínico na timeline.
- **id** (INT PK)
- **session_id** (FK sessions.id)
- **type** (VARCHAR) - Tipo de alerta (`clinical_risk`, `behavioral_risk`, `system_error`).
- **message** (VARCHAR) - Descrição legível para o usuário.
- **severity** (VARCHAR) - `info`, `warning`, `critical`.
- **is_dismissed** (BOOLEAN) - Controle de leitura.

### 2.6 Tabela `audit_logs`
Seguindo o regulamento de telemedicina e privacidade, cada ação do usuário é registrada em trilha inalterável.
- **id** (INT PK)
- **user_id** (FK users.id)
- **action** (VARCHAR) - Ação executada (ex: `view_session`, `download_report`).
- **resource** (VARCHAR) - Recurso acessado.
- **timestamp** (DATETIME)

## 3. Modelo Relacional
- Um **Usuário** gerencia Múltiplas **Sessões** (`1:N`).
- Uma **Sessão** possui Múltiplos **MediaFiles**, **Alerts**, **VideoAnalyses**, **AudioAnalyses**, e **DocumentAnalyses** (`1:N`).
- Uma **Sessão** gera um único **Score IGA**, que serve de alerta consolidado para os Dashboards.
