-- SafePlan Database Initialization Script
-- Executado automaticamente na primeira inicialização do container

-- Garantir que o usuário safeplan tem permissões adequadas
ALTER USER safeplan CREATEDB;
ALTER USER safeplan CREATEROLE;

-- Conceder privilégios ao usuário
GRANT ALL PRIVILEGES ON DATABASE safeplan_db TO safeplan;

-- Conectar ao banco safeplan_db
\connect safeplan_db

-- Criar schema public (se não existir)
CREATE SCHEMA IF NOT EXISTS public;
GRANT ALL ON SCHEMA public TO safeplan;

-- Log de inicialização
SELECT 'SafePlan Database initialized successfully' as status;
