-- =====================================================
-- GuardIA Parto Seguro — Inicialização dos Bancos de Domínio
-- Executado automaticamente pelo postgres-domains na 1ª inicialização
-- =====================================================

-- Cria os bancos para cada domínio (video_db já criado como POSTGRES_DB)
CREATE DATABASE audio_db;
CREATE DATABASE document_db;
CREATE DATABASE risk_db;
CREATE DATABASE report_db;
CREATE DATABASE security_db;

-- Garante privilégios do usuário guardia em todos os bancos
\connect audio_db
GRANT ALL PRIVILEGES ON DATABASE audio_db TO guardia;

\connect document_db
GRANT ALL PRIVILEGES ON DATABASE document_db TO guardia;

\connect risk_db
GRANT ALL PRIVILEGES ON DATABASE risk_db TO guardia;

\connect report_db
GRANT ALL PRIVILEGES ON DATABASE report_db TO guardia;

\connect security_db
GRANT ALL PRIVILEGES ON DATABASE security_db TO guardia;

