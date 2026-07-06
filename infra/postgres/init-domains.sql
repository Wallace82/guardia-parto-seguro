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


-- =========================================================================
-- SEED DE USUÁRIOS DE TESTE (APENAS PARA REFERÊNCIA SQL)
-- Nota Arquitetural: O 'core_db' roda em um container separado (postgres-core).
-- Como a tabela 'users' é criada dinamicamente via Alembic migrations quando o
-- backend inicia, este script (que roda antes das migrations) não pode criar 
-- os registros diretamente na primeira inicialização do banco.
-- 
-- O seed oficial e automático é feito pelo container 'core-api' via 'python seed.py'
-- após a execução das migrações.
-- =========================================================================

-- Para fins de referência ou importação manual direta no 'core_db':
/*
\connect core_db

INSERT INTO users (email, full_name, hashed_password, role, is_active)
VALUES 
  ('admin@guardia.com', 'Administrador GuardIA', '$2b$12$x8IJ1UF/gK54NfZNokN9/u8QwhluEKJvJ5LHfyjS.t0FoCG5q3hMC', 'admin', true),
  ('medico@guardia.com', 'Dr. João Silva (Profissional)', '$2b$12$x8IJ1UF/gK54NfZNokN9/u8QwhluEKJvJ5LHfyjS.t0FoCG5q3hMC', 'profissional', true),
  ('gestor@guardia.com', 'Dra. Maria Helena (Gestora)', '$2b$12$x8IJ1UF/gK54NfZNokN9/u8QwhluEKJvJ5LHfyjS.t0FoCG5q3hMC', 'gestor', true),
  ('auditor@guardia.com', 'Auditor Carlos Drummond', '$2b$12$x8IJ1UF/gK54NfZNokN9/u8QwhluEKJvJ5LHfyjS.t0FoCG5q3hMC', 'auditor', true)
ON CONFLICT (email) DO NOTHING;
*/

