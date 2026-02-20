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

---

## 🌐 Fase 2B - PI AF Server Integration (Completa ✅)

### Implementado

Integração completa com PI AF Server (SAURIOPIAF02) para leitura automatizada de sensores de fogo e gás do servidor Petrobras.

1. **Configuração AF Server**
   - `config/config_gideaopi.json`: Configuração para SAURIOPIAF02 e DB_BUZIOS_SENSORES

2. **Biblioteca gideaoPI Adaptada**
   - `src/pi_server/gideaoPI.py`: Adaptação da biblioteca Petrobras com logging e integração ConfiguraçãoI

3. **AF Database Manager**
   - `src/pi_server/af_manager.py`: Exploração e descoberta automatizada de sensores na hierarquia AF
   - Suporte para 8+ tipos de sensores: CH4, H2S, CO2, FLAME, SMOKE, TEMPERATURE, H2, O2
   - Organização por plataforma (P74-P79, FPAB, FPAT)

4. **Scripts de Integração**
   - `scripts/discover_sensor_paths.py`: Descobre sensores e gera mapeamento em JSON
   - `scripts/import_sensors_from_af.py`: Importa sensores com thresholds automáticos

5. **Documentação**
   - `docs/PI_AF_INTEGRATION.md`: Guia completo com instruções e troubleshooting

### Fluxo de Integração

```
[1] Conectar a SAURIOPIAF02 → DB_BUZIOS_SENSORES
    └─ python scripts/discover_sensor_paths.py
    └─ Gera config/sensor_paths_buzios.json com mapeamento

[2] Importar sensores para SafePlan
    └─ python scripts/import_sensors_from_af.py
    └─ Aplica thresholds automáticos por tipo
    └─ Cria regras de alerta (Warning + Critical)

[3] Verificar no Dashboard
    └─ streamlit run app/main.py
    └─ Configuration → List Sensors
```

### Thresholds Automáticos

Sensores importados com limites inteligentes baseados no tipo:

- **CH4:** 0 → 5 (warning) → 50 (danger) → 100 (critical) ppm
- **H2S:** 0 → 1 → 10 → 20 ppm
- **CO2:** 0 → 100 → 5000 → 10000 ppm
- **TEMPERATURE:** -10°C → 20 → 60 → 80°C
- **FLAME/SMOKE:** Escalas específicas (0-3)
- Outros: Configuáveis via UI

### Pré-requisitos

1. PI AF SDK instalado em `C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0`
2. Acesso à rede corporativa (SAURIOPIAF02 acessível)
3. Python 3.8+ com suporte a .NET assemblies (pythonnet/IronPython)

---

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
- **Fase 2B Guide:** `docs/PI_AF_INTEGRATION.md`
- **Database Schema:** `docs/DATABASE_SCHEMA.md`
- **Plano Detalhado:** Ver arquivo de plano

---

**Status:** Fase 2B (PI AF Server Integration) ✅
**Próximo:** Fase 3 (ML Integration)