# SafePlan Backend - FastAPI

Backend API para a migração de SafePlan de Streamlit para React + FastAPI.

## Estrutura do Projeto

```
backend/
├── main.py                 # Aplicação FastAPI principal
├── requirements.txt        # Dependências Python
├── pyproject.toml         # Configuração do projeto
├── .env.example           # Exemplo de variáveis de ambiente
│
├── config/
│   ├── __init__.py
│   └── settings.py        # Configurações e variáveis de ambiente
│
├── src/
│   ├── api/               # Rotas e endpoints FastAPI
│   ├── data/              # Data layer (modelos, repositórios)
│   ├── ml/                # Machine Learning (anomalias, forecast)
│   ├── sensors/           # Gerenciamento de sensores
│   ├── alerting/          # Engine de alertas
│   ├── scheduler/         # Tarefas agendadas (Celery)
│   └── utils/             # Utilitários e helpers
│
├── tests/
│   ├── unit/              # Testes unitários
│   └── integration/       # Testes de integração
│
└── migrations/            # Alembic migrations para banco de dados
```

## Pré-requisitos

- Python 3.10+
- PostgreSQL 14+
- Redis (opcional, para cache)

## Configuração Inicial

### 1. Criar Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas credenciais PostgreSQL
```

### 4. Configurar PostgreSQL

```bash
# Linux/Mac
createdb safeplan_db
createuser -P safeplan  # Enter password when prompted

# Windows (usando psql)
# psql -U postgres
# CREATE DATABASE safeplan_db;
# CREATE USER safeplan WITH PASSWORD 'your_password';
```

## Execução Local

```bash
# Desenvolvimento (com reload automático)
python main.py

# Ou com uvicorn diretamente
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API estará disponível em: http://localhost:8000

Documentação interativa (Swagger): http://localhost:8000/docs

## Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=backend tests/

# Apenas testes unitários
pytest tests/unit/

# Apenas integração
pytest tests/integration/
```

## Linting e Formatação

```bash
# Format com Black
black backend/

# Lint com Ruff
ruff check backend/

# Type check com mypy
mypy backend/ --ignore-missing-imports
```

## Próximas Etapas (Phase 1)

- [ ] Criar modelos de dados (SensorConfig, SensorReading)
- [ ] Implementar repositórios (CRUD operations)
- [ ] Criar rotas para sensores (GET, POST, PUT, DELETE)
- [ ] Criar rotas para leitura de dados
- [ ] Integrar com PI Server
- [ ] Implementar cache Redis
- [ ] Adicionar autenticação JWT
- [ ] Deploy com Docker

## Documentação

- [MIGRATION_ROADMAP_V2.md](../docs/MIGRATION_ROADMAP_V2.md) - Plano de 13 semanas
- [PHASE0_CHECKLIST.md](../docs/PHASE0_CHECKLIST.md) - Checklist de 48 horas
- [DATABASE_ANALYSIS_SQLITE_VS_POSTGRESQL.md](../docs/DATABASE_ANALYSIS_SQLITE_VS_POSTGRESQL.md) - Análise técnica
