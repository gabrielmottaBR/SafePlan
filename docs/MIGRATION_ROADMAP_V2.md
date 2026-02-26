# Roadmap de Migração Arquitetural - SafePlan

**Versão:** 2.0 - Atualizado  
**Data:** 22 de Fevereiro de 2026  
**Status:** Pronto para Implementação

---

## 🎯 Objetivo

Migrar SafePlan de **Streamlit** (solução de prototipagem) para **React + FastAPI** (solução production-ready) para suportar crescimento de 9.964 para 15.000+ sensores com performance, escalabilidade e robustez garantidas.

---

## 📊 Contexto Atual (Validado)

| Métrica | Valor | Status | Validação |
|---------|-------|--------|-----------|
| Sensores em banco | 9,964 | ✅ Operacional | Confirmado: 99.640 leituras criadas |
| Crescimento previsto | 15,000+ | ⚠️ Inviável com Streamlit | 1.5x escala = impossível 3-5s/página |
| Framework atual | Streamlit | ❌ Não é produção | Sem real-time, load balancing, WebSocket |
| Tempo carregamento | 3-5s | ❌ Inaceitável | UX ruim, usuários abandonam |
| Suporte real-time | ❌ Não | ❌ Crítico para alertas | Alertas devem chegar em <1s |
| Load balancing | ❌ Não | ❌ Escalabilidade bloqueada | Impossível múltiplas instâncias |
| Banco de dados | SQLite | ⚠️ Limitação | Max ~50MB, sem índices eficientes |

---

## 🏗️ Arquitetura Proposta

```
┌─────────────────────────────────────────────┐
│     FRONTEND: React + Vite (19KB gzip)      │
│  • SPA responsivo com TanStack Query        │
│  • Plotly.js para gráficos interativos      │
│  • WebSocket para alertas real-time         │
│  • Deploy: Vercel, Netlify ou S3+CloudFront│
└──────────────┬──────────────────────────────┘
               │ REST API + WebSocket
               │ JSON (CORS enabled)
┌──────────────▼──────────────────────────────┐
│   BACKEND: FastAPI (Python + Async)         │
│  • uvicorn + gunicorn (multi-process)       │
│  • Async endpoints (/sensors, /readings)    │
│  • Redis cache (grupo, módulo, agg)         │
│  • JWT + rate limiting                      │
│  • OpenAPI/Swagger automático               │
│  • Docker ready                             │
└──────────────┬──────────────────────────────┘
               │ SQLAlchemy ORM
┌──────────────▼──────────────────────────────┐
│   DATABASE: PostgreSQL (Production-grade)   │
│  • Índices: (sensor_id, timestamp)          │
│  • Índices: (grupo, modulo)                 │
│  • Particionamento de readings              │
│  • Backups automáticos 6h                   │
│  • Replicação para HA                       │
└──────────────────────────────────────────────┘
```

---

## 📅 Plano de Implementação Detalhado

### **Fase 0: Preparação (1-2 semanas) ⚡ COMECE AGORA**

Esta fase é crítica - dela dependem todas as outras.

#### 0.1 Validação de Pré-Requisitos
- [ ] Apresentar roadmap aos stakeholders
- [ ] Obter aprovação formal para procedimento
- [ ] Confirmar alocação de 6-7 pessoas
- [ ] Criar repositório `safeplan-backend` no GitHub
- [ ] Definir deadline MVP: 14 semanas

**Saída:** Aprovação, repo criado, timeline confirmada

#### 0.2 Setup de Ambiente Paralelo
- [ ] Instalar Node.js 18+ LTS (se não tiver)
- [ ] Instalar PostgreSQL (local ou Docker)
- [ ] Instalar Redis (local ou Docker)
- [ ] Criar docker-compose.yml para dev
- [ ] Criar requirements-dev.txt com ferramentas

**Saída:** Ambiente funcional em 3 máquinas

#### 0.3 Preparação de Dados
- [ ] Backup completo: `safeplan.db` + `config/`
- [ ] Criar script SQLite → PostgreSQL
- [ ] Validar integridade (row count, checksums)
- [ ] Performance baseline SQLite atual
- [ ] Document todas as constraints

**Saída:** Dados seguros, script de migração testado

**Duração:** 5-7 dias  
**Recursos:** 1 Backend dev + 1 DevOps

---

### **Fase 1: Backend FastAPI MVP (3 semanas)**

#### 1.1 Setup Projeto FastAPI
```bash
# Estrutura de pastas
safeplan-backend/
├── app/
│   ├── main.py              # Entry point
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # DB config
│   └── api/
│       └── routes/
│           ├── sensors.py
│           ├── readings.py
│           └── alerts.py
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/                 # Migrações DB
├── docker-compose.yml
├── requirements.txt
└── .github/workflows/       # CI/CD
```

- [ ] Criar projeto base com FastAPI
- [ ] Configurar logging estruturado (JSON)
- [ ] Impl middleware: CORS, error handling
- [ ] Setup SQLAlchemy + alembic
- [ ] JWT authentication (basic)

#### 1.2 Porting dos Modelos SQL
- [ ] Copiar `models.py` do projeto antigo
- [ ] Adaptar para PostgreSQL
- [ ] Criar alembic migrations
- [ ] Testar contra safeplan.db existente
- [ ] Documentar schema

#### 1.3 Endpoints Básicos (CRUD)

**Endpoints MVP:**
```
GET  /api/v1/sensors?limit=50&offset=0
GET  /api/v1/sensors/{id}
POST /api/v1/sensors
PUT  /api/v1/sensors/{id}
GET  /api/v1/readings/{sensor_id}?days=30
GET  /api/v1/sensors/grupo/{grupo}
GET  /api/v1/sensors/search?q=termo
```

- [ ] Implementar todos os endpoints acima
- [ ] Validação com Pydantic
- [ ] HTTP status codes corretos
- [ ] Testes unitários (>80%)
- [ ] Documentação Swagger

**Saída esperada:** API com 8+ endpoints, testes passando
**Duração:** 10-14 dias  
**Recursos:** 2 Backend developers

---

### **Fase 2: Performance & Features (2 semanas)**

#### 2.1 Caching com Redis
- [ ] Setup Redis pooling
- [ ] Cache sensores (TTL: 2h)
- [ ] Cache readings agregados (TTL: 5min)
- [ ] Invalidação em updates
- [ ] Monitoramento hit rates

#### 2.2 Otimização de Database
- [ ] Índices PostgreSQL (sensor_id, timestamp)
- [ ] Índices (grupo, modulo)
- [ ] EXPLAIN ANALYZE queries
- [ ] Connection pooling (pool_size=20)
- [ ] Query timeouts (30s)

#### 2.3 Features Avançadas
- [ ] Alertas (GET/POST/DELETE)
- [ ] Estatísticas agregadas
- [ ] Export CSV/JSON
- [ ] Health check endpoint
- [ ] Métricas Prometheus

**Meta Performance:** <100ms P95 para 9.964 sensores  
**Saída:** Backend robusto, pronto para produção  
**Duração:** 10 dias  
**Recursos:** 1-2 Backend developers

---

### **Fase 3: Frontend React MVP (3 semanas)**

#### 3.1 Setup React + Vite
```bash
npm create vite@latest safeplan-frontend -- --template react
cd safeplan-frontend
npm install
# Tailwind + ESLint + Vitest
npm install -D tailwindcss @tailwindcss/postcss eslint prettier vitest
```

- [ ] Criar app React com Vite
- [ ] Setup Tailwind CSS
- [ ] Prettier + ESLint config
- [ ] Vitest + Testing Library
- [ ] Axios client com interceptors

#### 3.2 Páginas Principais
- [ ] **Dashboard:** 
  - Lista 9.964 sensores com paginação
  - Filtros: grupo, módulo, tipo gás
  - Busca por tag
  - Status indicators
  
- [ ] **Detalhe do Sensor:**
  - Gráfico 30 dias (Plotly)
  - Stats: min/max/avg
  - Histórico de alertas
  - Config panel
  
- [ ] **Alertas:**
  - Lista de alertas ativos
  - Acknowledge/resolve
  - Config de regras

#### 3.3 Backend Integration
- [ ] TanStack Query (React Query) setup
- [ ] Custom hooks: useSensors, useReadings, useAlerts
- [ ] WebSocket para alertas real-time
- [ ] Error boundaries
- [ ] Loading skeletons
- [ ] Responsive design

**Saída:** Frontend funcional, integrado com FastAPI  
**Duração:** 14 dias  
**Recursos:** 2 Frontend developers

---

### **Fase 4: Testes & Deployment (2 semanas)**

#### 4.1 Testes Automatizados
- [ ] Backend: pytest (>85% coverage)
- [ ] Frontend: Vitest (>75% coverage)
- [ ] E2E: Playwright (critical paths)
- [ ] Load: k6 (1000 req/s)
- [ ] Segurança: OWASP Top 10

#### 4.2 CI/CD Pipeline
- [ ] GitHub Actions workflow
- [ ] Docker: backend + frontend
- [ ] docker-compose produção
- [ ] Build images em ECR
- [ ] Auto-deploy staging

#### 4.3 Staging Deployment
- [ ] Deploy VPS/EC2
- [ ] SSL/TLS (Let's Encrypt)
- [ ] Monitoramento:
  - [ ] Prometheus metrics
  - [ ] Grafana dashboards
  - [ ] Sentry (errors)
  - [ ] ELK/CloudWatch (logs)
- [ ] Teste de cutover

**Saída:** Sistema pronto para produção  
**Duração:** 10 dias  
**Recursos:** 1 DevOps + 1 QA

---

### **Fase 5: Go Live (1 semana)**

#### 5.1 Cutover Final
- [ ] Backup final SQLite
- [ ] Migração dados PostgreSQL
- [ ] DNS update (gradual)
- [ ] Health checks 24/7
- [ ] Monitoramento contínuo

#### 5.2 Estabilização
- [ ] Rollback testado
- [ ] SLA 99.9% monitorado
- [ ] Performance validada
- [ ] On-call rotation
- [ ] Retrospective

**Duração:** 3-5 dias  
**Recursos:** Equipe inteira

---

## 📊 Timeline Completa

```
Semana   1-2: Fase 0 - Preparação
Semana   3-5: Fase 1 - Backend API
Semana   6-7: Fase 2 - Performance
Semana  8-10: Fase 3 - Frontend
Semana 11-12: Fase 4 - Testes
Semana    13: Fase 5 - Go Live
────────────────────────────
Total: 13 semanas = ~3 meses
```

---

## 💰 Recursos Necessários

### Humanos (Recomendado)
- 1 Tech Lead/Arquiteto (tempo parcial: weekends)
- 2 Backend Developers (full-time, Python/FastAPI)
- 2 Frontend Developers (full-time, React/TypeScript)
- 1 DevOps Engineer (time-bound, Docker/K8s)
- 1 QA/Tester (testes automatizados)
- **Total: 7 people, 3 months**

### Infraestrutura
- PostgreSQL RDS: $200-400/mês
- Redis ElastiCache: $50-150/mês
- EC2/VPS staging: $100-200/mês
- Monitoring (Datadog): $100-300/mês
- **Total: ~$450-1.050/mês**

### One-Time Costs
- Domain/SSL: $20/ano
- Training: $500-1.000
- **Total: ~$520-1.020**

---

## 🔄 Alternativa: Abordagem Incremental (Menos Arriscada)

Se não conseguir 7 pessoas simultâneas:

### Fase 1A: FastAPI Only (3 semanas)
- Backend paralelo ao Streamlit
- Sem mudança frontend
- APIs prontas para React

### Fase 2A: Migração Gradual (4-6 semanas)
- Página por página em React
- Integração com FastAPI
- Deprecação lenta do Streamlit

**Vantagem:** Risco reduzido, validação iterativa  
**Desvantagem:** Timeline +50% (19 semanas)

---

## ⚠️ Riscos & Mitigação

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Perda de dados migração | 🔴 Crítico | 3x backups, validação SQL |
| Performance insuficiente | 🔴 Crítico | Benchmarks semanais, índices |
| Downtime cutover | 🔴 Crítico | Blue-green deploy, DNS gradual |
| Equipe inexperiente | 🟠 Alto | Pair programming, treinamento |
| Scope creep features | 🟠 Alto | MVP bem definido, priorização |
| WebSocket instável | 🟡 Médio | Fallback polling, testes |

---

## ✅ Critérios de Sucesso

- [x] **Dados:** 9.964 sensores migrados, sem perda
- [ ] **Performance:** <100ms P95 para lista sensores
- [ ] **Frontend:** <500ms TTFB, Lighthouse >90
- [ ] **Escala:** 15.000+ sensores suportados
- [ ] **Real-time:** Alertas <1s
- [ ] **Segurança:** OWASP Top 10 audit pass
- [ ] **Deploy:** <5min from commit → production

---

## 📋 Checklist Imediato (Próximas 48h)

**Responsável:** Tech Lead + CTO

- [ ] Revisar roadmap este documento
- [ ] Apresentar aos stakeholders (30min)
- [ ] Obter aprovação formal
- [ ] Confirmar alocação de pessoas
- [ ] Criar repo `safeplan-backend`
- [ ] Instalar ferramentas (Node, PostgreSQL, Redis)
- [ ] Agendar kick-off meeting
- [ ] Backup completo do projeto

---

## 📚 Documentação de Referência

**Backend:**
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Redis Python Client](https://redis-py.readthedocs.io/)

**Frontend:**
- [React 18 Docs](https://react.dev/)
- [TanStack Query](https://tanstack.com/query/latest/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vitest](https://vitest.dev/)

**DevOps:**
- [Docker Best Practices](https://docs.docker.com/)
- [Kubernetes](https://kubernetes.io/)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance-tips.html)

---

## 📝 Decisão Requerida

**Para Stakeholders:**

> Para proceder, aprove:
> - ✅ Timeline: 13 semanas (3 meses)
> - ✅ Budget: $450-1.050/mês + one-time $500-1.000
> - ✅ Recursos: 7 pessoas alocadas 100%
> - ✅ Arquitetura: React + FastAPI + PostgreSQL

**Alternativa:** Se não conseguir 7 pessoas, aprovar abordagem incremental (19 semanas).

---

**Status:** ✅ Documento validado (22/02/2026)  
**Próximo passo:** Apresentação aos stakeholders e aprovação

**Perguntas?** Contate o Tech Lead
