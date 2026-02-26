# Checklist de Preparação para Migração - Fase 0

**Data Início:** 22 de Fevereiro de 2026  
**Deadline Fase 0:** 28 de Fevereiro de 2026 (6 dias)  
**Responsável Geral:** Tech Lead  
**Status:** 🔴 NOT STARTED

---

## 🎯 Objetivo Fase 0

Validar viabilidade, obter aprovação, configurar ambiente paralelo, preparar dados.

**Resultado esperado:** Time pronto para começar Fase 1 (Backend) no dia 01/03/2026

---

## 📋 Checklist de 48 horas (Imediato)

### ✋ STOP: Ler Documentação Primeiro

**Responsável:** CTO + Tech Lead  
**Tempo:** 1 hora  
**Deadline:** FRI 22/02 EOB

- [ ] Ler EXECUTIVE_SUMMARY.md (5 min)
- [ ] Ler MIGRATION_ASSESSMENT.md (10 min)
- [ ] Ler seção "Arquitetura Proposta" (10 min)
- [ ] Fazer 1-2 perguntas (se houver dúvidas)
- [ ] Confirmar entendimento (check box abaixo)

**✅ Checkbox:** Documentação entendida e validada

---

### 1️⃣ Apresentação aos Stakeholders

**Responsável:** CTO  
**Participantes:** Liderança técnica, financeira, produto  
**Tempo:** 30-45 minutos  
**Deadline:** SAT 23/02 ou MON 25/02

**Agenda:**
1. Contexto atual + limitações Streamlit (5 min)
2. Proposta: React + FastAPI (10 min)
3. Timeline: 13 semanas (2 min)
4. Budget: $1.050/mês (2 min)
5. Recursos: 7 pessoas (2 min)
6. Riscos & mitigação (5 min)
7. Q&A (10 min)

**Materiais:**
- [ ] Imprimir EXECUTIVE_SUMMARY.md
- [ ] Slide 1: Current limitations (Streamlit 3-5s)
- [ ] Slide 2: Proposed solution (React 500ms)
- [ ] Slide 3: Timeline & resources
- [ ] Slide 4: ROI calculation

**Saída esperada:** ✅ Aprovação formal (email)

**Checkbox:** Aprovação obtida (print screen email)

---

### 2️⃣ Confirmação de Recursos

**Responsável:** Tech Lead + HR/PM  
**Deadline:** MON 25/02

Confirmar alocação de **7 pessoas full-time**:

- [ ] 2 Backend developers (Python/FastAPI)
  - [ ] Dev 1: ___________
  - [ ] Dev 2: ___________
  
- [ ] 2 Frontend developers (React/TypeScript)
  - [ ] Dev 3: ___________
  - [ ] Dev 4: ___________
  
- [ ] 1 DevOps engineer (Docker/K8s)
  - [ ] DevOps: ___________
  
- [ ] 1 QA/Tester (testes automatizados)
  - [ ] QA: ___________
  
- [ ] 1 Tech Lead coordenador (part-time weekends)
  - [ ] Lead: ___________

**Validação**
- [ ] Todos confirmaram 100% dedic por 3 meses?
- [ ] Calendário bloqueado (no other projects)?
- [ ] Vacation schedule revisado (sem gaps)?

**Checkbox:** Todos 7 recursos confirmados

---

### 3️⃣ Criação de Repositório Backend

**Responsável:** DevOps  
**Deadline:** MON 25/02

- [ ] Create GitHub repo: `safeplan-backend`
- [ ] Settings:
  - [ ] Visibility: Private
  - [ ] Default branch: `main`
  - [ ] Branch protection: require reviews
  - [ ] Require status checks before merge
  
- [ ] Initial files:
  - [ ] README.md (blank, será preenchido)
  - [ ] .gitignore (Python template)
  - [ ] requirements.txt (empty)
  - [ ] pyproject.toml (empty)
  
- [ ] GitHub Actions:
  - [ ] Create `.github/workflows/`
  - [ ] Create `ci.yml` template (will be filled week 1)

- [ ] Add team members as collaborators
  - [ ] 2 Backend devs (write access)
  - [ ] DevOps (admin)
  - [ ] Tech Lead (admin)

**Repository URL:** `https://github.com/[org]/safeplan-backend`

**Checkbox:** Repo criado e team adicionado

---

### 4️⃣ Setup Environment

**Responsável:** DevOps + Backend devs  
**Deadline:** TUE 26/02

#### Instalar Dependências (se não tiver)

**Node.js:**
```bash
# Check if installed
node --version  # Must be 18+ LTS

# If not installed:
# Linux/Mac: Use nvm
# Windows: Download from nodejs.org
```
- [ ] Node 18+ LTS instalado
- [ ] npm ou yarn funcional

**PostgreSQL:**
```bash
# Option 1: Local install (or)
# Option 2: Docker
docker run --name safeplan-db \
  -e POSTGRES_PASSWORD=dev123 \
  -p 5432:5432 \
  -d postgres:15
```
- [ ] PostgreSQL 15+ rodando
- [ ] Acessível em localhost:5432
- [ ] Senha padrão: `dev123`

**Redis:**
```bash
# Option 1: Docker (recomendado)
docker run --name safeplan-redis \
  -p 6379:6379 \
  -d redis:7-alpine
```
- [ ] Redis 7+ rodando
- [ ] Acessível em localhost:6379
- [ ] Sem senha (dev mode)

**Docker & Docker Compose:**
- [ ] Docker instalado (Windows/Mac: Docker Desktop)
- [ ] docker-compose ou docker compose
- [ ] Pode fazer `docker run` com sucesso

**Python:**
```bash
# Verify Python 3.11+
python --version

# Create venv for safeplan-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
- [ ] Python 3.11+ instalado
- [ ] venv criado e ativado

---

### 5️⃣ Data Preparation & Backup

**Responsável:** Backend dev + DevOps  
**Deadline:** TUE 26/02

**Backup do Projeto Atual:**

```bash
cd ~/Documents/GitHub

# Full backup
cp -r SafePlan SafePlan.backup.2026-02-22
tar -czf SafePlan.backup.2026-02-22.tar.gz SafePlan.backup/
```

- [ ] Backup completo de SafePlan/
- [ ] Backup compactado (tar.gz)
- [ ] Armazenado em local seguro
- [ ] Size: ~500MB (document size)

**Backup do Banco de Dados:**

```bash
# SQLite backup
cp safeplan.db safeplan.db.backup.2026-02-22

# Validate backup
sqlite3 safeplan.db.backup.2026-02-22 "SELECT COUNT(*) FROM sensor_config;"
# Expected: 9964
```

- [ ] safeplan.db backup criado
- [ ] Validado: 9.964 sensors
- [ ] Validado: 99.640 readings
- [ ] Backup armazenado duplicado

**SQL Dump (para migração):**

```bash
# Export schema
sqlite3 safeplan.db ".schema" > schema.sql

# Export data (or use Python migration script)
```

- [ ] Schema exported to schema.sql
- [ ] Data validation script criado

**PostgreSQL Migration Script (Python):**

```python
# scripts/migrate_sqlite_to_postgres.py
# Será criado na Fase 1, mas preparar checklist aqui
```

- [ ] Script criado (Fase 1 tarefa 1.2)
- [ ] Testado contra backup
- [ ] Generate test report

---

### 6️⃣ docker-compose.yml para Dev

**Responsável:** DevOps  
**Deadline:** WED 27/02

Criar arquivo: `docker-compose.dev.yml`

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: safeplan
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

- [ ] docker-compose.dev.yml criado
- [ ] Testado: `docker-compose -f docker-compose.dev.yml up`
- [ ] PostgreSQL accessible: `psql -h localhost -U dev -d safeplan`
- [ ] Redis accessible: `redis-cli -h localhost ping`
- [ ] Documented no README

---

### 7️⃣ Meeting: Kick-off Técnico

**Responsável:** Tech Lead  
**Participantes:** Todos 7 + stakeholders (optional)  
**Tempo:** 2 horas  
**Deadline:** THU 27/02 ou FRI 28/02

**Agenda:**

1. **Visão Geral (15 min)**
   - Roadmap 13 semanas
   - Arquitetura proposta
   - Timeline faseado

2. **Responsabilidades (20 min)**
   - Quem faz o quê?
   - Dependências entre times
   - Communication protocol

3. **Tecnologias (20 min)**
   - Stack: Python/FastAPI/React
   - Conventions: naming, testing, docs
   - Enforce: BOT_RULES.md

4. **Infraestrutura (15 min)**
   - Local dev environment
   - Staging setup
   - Production plan

5. **CI/CD & Workflow (15 min)**
   - Git workflow (branches, PRs)
   - Code reviews
   - Testing requirements

6. **Weekly Cadence (10 min)**
   - Daily standup: 9:30 AM
   - Weekly demo: Friday 4 PM
   - Retrospective: End of sprint
   - Escalation path

7. **Q&A (25 min)**

**Documents to Share:**
- [ ] MIGRATION_ROADMAP_V2.md (print copies)
- [ ] Arquitetura diagram
- [ ] BOT_RULES.md (código standards)

**Checkbox:** Kick-off realizado, todos aligned

---

## 📋 Checklist Estendido: Semana 1 (Phase 0 Complete)

### SUN 28/02 EOB: Phase 0 Validation

- [ ] Documentação: 100% lida e entendida
- [ ] Stakeholders: Aprovação formal (email)
- [ ] Recursos: 7 pessoas confirmadas
- [ ] Backend Repo: Criado e team adicionado
- [ ] Environment: Node, PostgreSQL, Redis rodando
- [ ] Backups: Projeto e banco seguros
- [ ] docker-compose: Tested e funcional
- [ ] Kick-off: Meeting realizado, alinhados

**✅ GO/NO-GO Decision:**

If all checkboxes above are ✅ → **GO TO PHASE 1**
If any ❌ → **FIX & RETRY**

---

## 📞 Escalation & Support

**Tech Lead** (daily coordination):
- Resolve blockers
- Ensure timeline
- Report to CTO

**CTO** (weekly review):
- Approve decisions
- Remove obstacles
- Stakeholder updates

**DevOps** (infrastructure):
- Setup environments
- CI/CD pipeline
- Production plan

**Contacts:**
- Tech Lead: ___________
- CTO: ___________
- DevOps: ___________

---

## 📊 Status Dashboard

```
Phase 0: Preparation (Feb 22 - Feb 28)
├─ [ ] Documentation (FRI 22)
├─ [ ] Stakeholder approval (MON 25)
├─ [ ] Resource confirmation (MON 25)
├─ [ ] Backend repo (MON 25)
├─ [ ] Environment setup (TUE 26)
├─ [ ] Data backup (TUE 26)
├─ [ ] docker-compose (WED 27)
├─ [ ] Kick-off meeting (THU/FRI 27-28)
└─ [ ] GO/NO-GO decision (SUN 28)

Phase 1: Backend (Mar 1 - Mar 21)
Phase 2: Performance (Mar 22 - Apr 4)
Phase 3: Frontend (Apr 5 - Apr 25)
Phase 4: Testing (Apr 26 - May 9)
Phase 5: Go-Live (May 10 - May 16)
```

---

## 🎯 Success Metrics for Phase 0

- ✅ Aprovação formal de todas as partes
- ✅ 7 pessoas 100% dedicadas
- ✅ Ambiente local funcional (toda equipe)
- ✅ Backups validados
- ✅ Team aligned e motivado
- ✅ Documentação clara

---

**Documento:** Checklist de Preparação - Fase 0  
**Data:** 22 de Fevereiro de 2026  
**Responsável:** Tech Lead  
**Status:** 🔴 NOT STARTED → 🟡 IN PROGRESS → 🟢 COMPLETE

**Next Review:** February 28, 2026 (Go/No-Go Decision)
