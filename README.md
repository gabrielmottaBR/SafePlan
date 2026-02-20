# SafePlan - Plataforma de Monitoramento de Sensores de Fogo e Gás

SafePlan é um dashboard interativo profissional para monitoramento em tempo quasi-real de sensores de fogo e gás em plataformas Petrobras. A plataforma integra dados do PI Server, aplica Machine Learning para detecção de anomalias, gerencia alertas automáticos e integra notificações com Microsoft Teams.

## 📊 Visão Geral

**Objetivo:** Monitorar sensores de fogo e gás nas plataformas P74-P79, FPAB, FPAT (e futuramente P80-P83) com alertas inteligentes baseados em thresholds, anomalias e previsões.

**Tecnologia:**
- **Frontend/Backend:** Streamlit
- **Database:** SQLite (protótipo, escalável para PostgreSQL/SQL Server)
- **Data Source:** PI Server via gideaoPI
- **ML:** scikit-learn (Anomaly Detection) + Prophet (Forecasting)
- **Scheduler:** APScheduler
- **Reporting:** PDF, Excel

## 🚀 Fase 1 - Foundation (Completa ✅)

### Implementado

1. **Data Layer - Models & Database**
   - `src/data/models.py`: Modelos SQLAlchemy ORM
   - `src/data/database.py`: Gerenciamento de conexão SQLite
   - `src/data/repositories.py`: Padrão DAO com repositórios específicos

2. **Configuração Centralizada**
   - `config/settings.py`: Configuration via environment variables

3. **PI Server Integration**
   - `src/pi_server/pi_client.py`: Wrapper around gideaoPI
   - `src/pi_server/data_fetcher.py`: Ingestão de dados

4. **Database Initialization**
   - `scripts/init_db.py`: Script para criar schema

5. **Unit Tests**
   - `tests/unit/test_data_layer.py`: Testes básicos

---

## 🚀 Fase 2 - Core Alerting (Completa ✅)

### Implementado

1. **Alert Engine** (`src/alerting/alert_engine.py`)
   - State machine: ACTIVE → ACKNOWLEDGED → RESOLVED
   - Threshold-based alerting
   - 4 níveis de severidade (OK, Warning, Danger, Critical)
   - Deduplicação automática de alertas

2. **Teams Integration** (`src/alerting/teams_notifier.py`)
   - Adaptive Card formatting
   - Retry logic com exponential backoff
   - Webhook connectivity testing
   - Notification logging

3. **Sensor Manager** (`src/sensors/sensor_manager.py`)
   - CRUD para sensores
   - Alert rule creation/management
   - Multi-platform support (P74-P79, FPAB, FPAT)
   - 9+ tipos de sensores

4. **Streamlit Dashboard** (`app/main.py`)
   - Multi-page application (6 páginas)
   - Dashboard: real-time metrics
   - Alerts: gerenciamento de alertas
   - Configuration: sensor setup
   - DevTools: debugging

5. **Integration Tests**
   - `scripts/test_phase2.py`: Testes end-to-end

## 🔧 Como Usar

### 1. Setup Inicial

```bash
# Clone e configure
cd SafePlan
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt
```

### 2. Configuração

```bash
# Copie o template
cp .env.example .env

# Edite .env com suas credenciais
```

### 3. Inicialize o Banco

```bash
python scripts/init_db.py
```

### 4. Execute Testes (Fase 1)

```bash
python -m pytest tests/unit/test_data_layer.py -v
```

### 5. Execute Testes de Integração (Fase 2)

```bash
python scripts/test_phase2.py
```

### 6. Inicie o Dashboard

```bash
streamlit run app/main.py
```

Acesse: http://localhost:8501

---

## 📅 Próximas Fases

- **Fase 3:** ML Integration (Anomaly Detection, Forecasting)
- **Fase 4:** Advanced UI & Reporting
- **Fase 5:** Scheduling & Automation
- **Fase 6:** Deployment & Hardening

## 📚 Documentação

- **Fase 1 Guide:** `docs/ARCHITECTURE.md`
- **Fase 2 Guide:** `docs/PHASE2_GUIDE.md`
- **Database Schema:** `docs/DATABASE_SCHEMA.md`
- **Plano Detalhado:** Ver arquivo de plano

---

**Status:** Fase 2 (Core Alerting) ✅
**Próximo:** Fase 3 (ML Integration)