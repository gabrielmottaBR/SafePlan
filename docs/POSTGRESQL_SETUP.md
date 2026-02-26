# PostgreSQL Setup para SafePlan Backend

PostgreSQL não foi detectado no PATH. Escolha uma das opções abaixo:

## Opção 1: PostgreSQL Local (Windows)

### Instalação

1. **Download PostgreSQL 14+**
   - Acesse: https://www.postgresql.org/download/windows/
   - Selecione versão 14, 15, ou 16

2. **Executar instalador**
   - Próximo, Próximo...
   - Quando solicitado "Database Cluster", use `safeplan_db`
   - Defina senha do superuser (salve em local seguro)
   - Porta padrão: 5432

3. **Adicionar PATH (se necessário)**
   ```powershell
   # PowerShell como Admin
   $env:Path += ";C:\Program Files\PostgreSQL\16\bin"
   # Ou adicione permanentemente em System Properties > Environment Variables
   ```

4. **Verificar instalação**
   ```powershell
   psql --version
   # Deve mostrar: psql (PostgreSQL) 16.x
   ```

5. **Criar banco SafePlan**
   ```powershell
   # Conectar como superuser
   psql -U postgres
   
   # Dentro do psql:
   CREATE DATABASE safeplan_db;
   CREATE USER safeplan WITH PASSWORD 'safeplan_dev_password';
   ALTER ROLE safeplan CREATEDB;
   GRANT ALL PRIVILEGES ON DATABASE safeplan_db TO safeplan;
   \q
   ```

6. **Testar conexão**
   ```powershell
   psql -U safeplan -d safeplan_db -h localhost -p 5432
   # Deve conectar com sucesso
   \q
   ```

---

## Opção 2: PostgreSQL via Docker (Recomendado)

Mais rápido, sem instalações locais, pronto para produção.

### Pré-requisitos

- Docker Desktop instalado: https://www.docker.com/products/docker-desktop

### Criar docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: safeplan-postgres
    environment:
      POSTGRES_DB: safeplan_db
      POSTGRES_USER: safeplan
      POSTGRES_PASSWORD: safeplan_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U safeplan"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Iniciar PostgreSQL

```powershell
# No diretório do projeto (ou backend/)
docker-compose up -d

# Verificar status
docker-compose ps
# Deve mostrar: safeplan-postgres ... healthy
```

### Parar PostgreSQL

```powershell
docker-compose down
```

### Acessar banco de dados

```powershell
# Conectar com psql (se instalado) ou cliente gráfico
psql -U safeplan -d safeplan_db -h localhost -p 5432

# Ou use DBeaver como cliente gráfico
# https://dbeaver.io/download/
```

---

## Verificar Conectividade

```python
# Executar script de teste
python .\backend\test_db_connection.py

# Ou manualmente:
from sqlalchemy import text, create_engine

engine = create_engine(
    "postgresql+psycopg2://safeplan:safeplan_dev_password@localhost:5432/safeplan_db"
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("✓ Conexão bem-sucedida!")
```

---

## Próximas Etapas

Após configurar PostgreSQL:

1. Criar modelos SQLAlchemy (SensorConfig, SensorReading)
2. Criar migrations com Alembic
3. Executar migrations
4. Testar CRUD operations
5. Integrar com frontend React

---

## Troubleshooting

### Erro: "FATAL: password authentication failed"
- Verifique credenciais em `.env`
- Resete senha: `ALTER USER safeplan WITH PASSWORD 'new_password';`

### Erro: "could not translate host name"
- Use `localhost` em vez de `127.0.0.1`
- Verifique HOST em `.env`

### Porta 5432 já em uso
- Mude porta em docker-compose: `"5433:5432"`
- Ou matem processo: `netstat -ano | findstr :5432`

### Docker container não inicia
- Execute: `docker-compose logs postgres`
- Verifique espaço em disco
- Tente: `docker-compose restart`
