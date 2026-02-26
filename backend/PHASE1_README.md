# SafePlan Backend Phase 1 - Development Guide

## Início Rápido (5 minutos)

### 1. Ativar ambiente
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
source venv/bin/activate     # Linux/Mac
```

### 2. Iniciar servidor
```bash
python main.py
# ou
uvicorn backend.main:app --reload --port 8000
```

### 3. Acessar API
- **API**: http://localhost:8000
- **Documentação (Swagger)**: http://localhost:8000/docs
- **Documentação (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Rotas API Disponíveis (Phase 1)

### Sensores - Listagem
```
GET /api/v1/sensors/
  Query params: skip=0, limit=100
  Response: { total, skip, limit, data: [...] }
```

### Sensores - Contagem
```
GET /api/v1/sensors/count
  Response: { total_sensors, by_type: {...}, by_location: {...} }
```

### Sensores - Detalhe
```
GET /api/v1/sensors/{sensor_id}
  Response: SensorConfigResponse
```

### Sensores - Leituras
```
GET /api/v1/sensors/{sensor_id}/readings?hours=24&limit=100
  Query params: hours=24 (1-720), limit=100 (1-1000)
  Response: List[SensorReadingResponse]
```

### Sensores - Última Leitura
```
GET /api/v1/sensors/{sensor_id}/latest
  Response: SensorReadingResponse
```

### Sensores - Estatísticas
```
GET /api/v1/sensors/{sensor_id}/stats?hours=24
  Response: SensorStatsResponse (min, max, avg, count)
```

### Sensores - Por Localização
```
GET /api/v1/sensors/by-location/{location}
  Response: List[SensorConfigResponse]
```

### Sensores - Por Tipo
```
GET /api/v1/sensors/by-type/{sensor_type}
  Response: List[SensorConfigResponse]
```

### Sensores - Por Grupo (Votação)
```
GET /api/v1/sensors/by-group/{grupo}
  Response: List[SensorConfigResponse]
```

### Sensores - Por Módulo
```
GET /api/v1/sensors/by-module/{modulo}
  Response: List[SensorConfigResponse]
```

---

## Exemplos de Uso (cURL/PowerShell)

### Listar sensores (primeiros 10)
```bash
curl "http://localhost:8000/api/v1/sensors/?skip=0&limit=10" | jq
```

### Contar sensores
```bash
curl "http://localhost:8000/api/v1/sensors/count" | jq
```

### Detalhe de sensor
```bash
curl "http://localhost:8000/api/v1/sensors/SENSOR_001" | jq
```

### Leituras dos últimos 24h
```bash
curl "http://localhost:8000/api/v1/sensors/SENSOR_001/readings?hours=24" | jq
```

### Estatísticas (média, min, max)
```bash
curl "http://localhost:8000/api/v1/sensors/SENSOR_001/stats?hours=24" | jq
```

### Sensores por tipo
```bash
curl "http://localhost:8000/api/v1/sensors/by-type/O2" | jq
```

---

## Migrar Dados (Importante!)

Antes de usar a API, migre dados do banco legado:

```bash
# Ativar venv
.\backend\venv\Scripts\Activate.ps1

# Correr script de migração
python backend/scripts/migrate_data.py

# Ou com opções personalizadas
python backend/scripts/migrate_data.py \
  --source ../safeplan.db \
  --target safeplan.db
```

### Depois da migração:
- ✅ 9,964 sensores importados
- ✅ 99,640 leituras importadas
- ✅ API pronta para consultas

---

## Estrutura de Código

```
backend/
├── main.py                          # FastAPI app entry point
├── config/
│   └── settings.py                  # Pydantic settings (env vars)
├── src/
│   ├── api/
│   │   └── sensors.py               # Sensor endpoints (11 rotas)
│   ├── data/
│   │   ├── models.py                # SQLAlchemy models (6 tabelas)
│   │   ├── database.py              # DB config (SQLite/PostgreSQL)
│   │   ├── base_repository.py       # Generic CRUD base class
│   │   ├── sensor_repository.py     # Sensor CRUD + queries
│   │   ├── reading_repository.py    # Reading CRUD + stats
│   │   └── alert_repository.py      # Alert CRUD
│   ├── ml/                          # Anomaly detection, forecasting (Phase 2)
│   ├── alerting/                    # Alert engine (Phase 2)
│   ├── scheduler/                   # Background tasks (Phase 2)
│   └── utils/                       # Helpers, logging (Phase 2)
├── tests/
│   ├── unit/                        # Unit tests (Phase 2)
│   └── integration/                 # Integration tests (Phase 2)
└── scripts/
    └── migrate_data.py              # Data migration script
```

---

## Testes (Manual)

### Health Check
```bash
curl http://localhost:8000/health
# Response: { "status": "healthy", "service": "safeplan-backend", "environment": "development" }
```

### API Info
```bash
curl http://localhost:8000/
# Response: { "name": "SafePlan Backend API", "version": "2.0.0", "database": "SQLite (MVP)" }
```

### Database Stats
```bash
curl http://localhost:8000/stats
# Response: { "sensors_total": 9964, "readings_total": 99640, "database": "SQLite (MVP)" }
```

---

## Próximas Etapas (Phase 1 Continuação)

- [ ] **Testes Unitários** (pytest)
  - Test repositories CRUD
  - Test endpoints com mock data
  
- [ ] **Rotas de Alertas** (AlertRule, AlertEvent)
  - GET /api/v1/alerts/
  - POST /api/v1/alerts/
  - GET /api/v1/alerts/unresolved
  
- [ ] **Autenticação** (JWT)
  - POST /api/v1/auth/login
  - GET /api/v1/auth/me
  
- [ ] **Integração PI Server**
  - Endpoint para descobrir novos sensores
  - Fetch valores em tempo real
  
- [ ] **Cache Redis** (Opcional)
  - Cache /api/v1/sensors/count
  - Cache últimas leituras

---

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'backend'"
```bash
# Certifique-se de rodar do diretório raiz
cd C:\Users\EK40\OneDrive - PETROBRAS\Documents\GitHub\SafePlan
python backend/main.py
```

### Erro: "database is locked"
```bash
# SQLite tem limitations com escrita concorrente
# Solução: Usar PostgreSQL em produção (Phase 2)
```

### Porta 8000 já em uso
```bash
# Mudar porta
python main.py --port 8001
# ou
uvicorn backend.main:app --port 8001 --reload
```

### Dados não aparecem após migração
```bash
# Verificar se migração rodou
python backend/scripts/migrate_data.py --skip-readings

# Verificar stats
curl http://localhost:8000/stats
```

---

## Comandos Úteis

```bash
# Listar rotas
python -c "from backend.main import app; [print(r.path) for r in app.routes if hasattr(r, 'path')]"

# Testar database
python backend/scripts/migrate_data.py

# Rodar testes (quando disponíveis)
pytest backend/tests/unit/ -v

# Format código
black backend/

# Lint código
ruff check backend/

# Type check
mypy backend/ --ignore-missing-imports
```

---

**Status Phase 1:** MVP Backend com 11 endpoints, 4 repositórios, SQLite operacional  
**Próxima Checkpoint:** Integração com dados + testes unitários  
**Data Alvo:** March 3, 2026
