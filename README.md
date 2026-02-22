# SafePlan - Plataforma de Monitoramento de Sensores de Fogo e Gás

SafePlan é um dashboard interativo profissional para monitoramento em tempo quasi-real de sensores de fogo e gás em plataformas Petrobras. A plataforma integra dados do PI Server, aplica Machine Learning para detecção de anomalias, gerencia alertas automáticos e integra notificações com Microsoft Teams.

## 📊 Visão Geral

**Objetivo:** Monitorar sensores de fogo e gás nas plataformas P74-P79, FPAB, FPAT (e futuramente P80-P83) com alertas inteligentes baseados em thresholds, anomalias e previsões.

**Tecnologia:**
- **Frontend/Backend:** Streamlit
- **Database:** SQLite (protótipo, escalável para PostgreSQL/SQL Server)
- **Data Source:** PI Server via gideao_pi
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
   - `src/pi_server/pi_client.py`: Wrapper around gideao_pi
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

## � Quick Start (Comece em 5 minutos)

```bash
# 1. Clone e ativa venv
git clone <repo> && cd SafePlan
python -m venv venv
.\venv\Scripts\activate.ps1

# 2. Instala dependências
pip install -r requirements.txt

# 3. Inicializa banco e dados
python scripts/init_db.py
python scripts/create_sample_data.py

# 4. Inicia dashboard
streamlit run app/main.py

# 5. Acessa em seu navegador
# http://localhost:8501
```

**Pronto!** Dashboard com 11 sensores de exemplo, 1.848 leituras e alertas configurados.

---

## 🔍 Troubleshooting Comum

| Problema | Solução |
|----------|---------|
| **ModuleNotFoundError: No module named 'src'** | Execute de dentro da pasta raiz do projeto, não de subpastas |
| **database.db não criado** | Execute `python scripts/init_db.py` |
| **Streamlit não abre em localhost:8501** | Verifique se porta 8501 não está em uso: `netstat -ano \| findstr :8501` |
| **ImportError: No module named 'clr'** | Instale pythonnet: `pip install pythonnet` (necessário apenas para PI AF) |
| **Erro ao conectar SAURIOPIAF02** | Verifique acesso à rede corporativa e AF SDK instalado |

---

## 📋 Checklist de Configuração

- [ ] Python 3.13.7+ instalado
- [ ] Venv criado e ativado
- [ ] requirements.txt instalado
- [ ] .env configurado (se usando variáveis personalizadas)
- [ ] Database inicializado (`scripts/init_db.py`)
- [ ] Dados de exemplo criados (opcional)
- [ ] Dashboard iniciado com sucesso
- [ ] pythonnet instalado (se usando PI AF)
- [ ] Sensores descobertos e importados (se usando PI AF)

---

### Implementado

Integração completa com PI AF Server (SAURIOPIAF02) para leitura automatizada de sensores de fogo e gás do servidor Petrobras.

1. **Configuração AF Server**
   - `config/config_gideaopi.json`: Configuração para SAURIOPIAF02 e DB_BUZIOS_SENSORES

2. **Biblioteca gideao_pi Adaptada**
   - `src/pi_server/gideao_pi.py`: Adaptação da biblioteca Petrobras com logging e integração ConfiguraçãoI

3. **AF Database Manager**
   - `src/pi_server/af_manager.py`: Exploração e descoberta automatizada de sensores na hierarquia AF
   - Suporte para 8+ tipos de sensores: CH4, H2S, CO2, FLAME, SMOKE, TEMPERATURE, H2, O2
   - Organização por plataforma (P74-P79, FPAB, FPAT)

4. **Scripts de Integração**
   - `scripts/discover_sensor_paths.py`: Descobre sensores e gera mapeamento em JSON
   - `scripts/import_sensors_from_af.py`: Importa sensores com thresholds automáticos

5. **Documentação**
   - `docs/PI_AF_INTEGRATION.md`: Guia completo com instruções e troubleshooting

### Fluxo de Integração com PI AF Server

**Passo 1: Descobrir Sensores**
```bash
# Conecta a SAURIOPIAF02\DB_BUZIOS_SENSORES e navega pela estrutura:
# Buzios → {UEP} → Sensores → {MODULO} → {MODULO_ZONA} → {MODULO_ZONA_TIPO_GAS} → {TAG_DO_SENSOR}

python scripts/discover_sensor_paths.py

# Gera: config/sensor_paths_buzios.json com mapeamento de todos os sensores
# Espera: 5-10 minutos para 5000+ sensores
```

**Passo 2: Importar para SafePlan**
```bash
# Lê arquivo discover e importa para banco SQLite
# Aplica thresholds automáticos por tipo (CH4, H2S, CO2, etc)
# Cria 2 regras de alerta por sensor (Warning + Critical)

python scripts/import_sensors_simple.py

# Resultado: Sensores disponíveis no dashboard
```

**Passo 3: Verificar no Dashboard**
```bash
streamlit run app/main.py

# Vá para: Configuration → List Sensors
# Deve listar todos os sensores importados com thresholds
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

**Para Fases 1, 2, 3 (Local):**
- Python 3.13.7+
- pip (gerenciador de pacotes Python)
- 500MB espaço em disco (dependências + banco de dados)

**Para Fase 2B (PI AF Integration):**
1. ✅ PI AF SDK instalado em `C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0`
2. ✅ pythonnet instalado: `pip install pythonnet`
3. ✅ Acesso à rede corporativa (SAURIOPIAF02 acessível)
4. ✅ Credenciais de acesso ao AF Server

---

## 🔧 Como Usar

### 1. Setup Inicial do Projeto

```bash
# Clone o repositório
git clone <repository-url>
cd SafePlan

# Crie e ative o ambiente virtual
python -m venv venv

# No Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# No Windows (Command Prompt)
venv\Scripts\activate.bat

# No Linux/Mac
source venv/bin/activate

# Instale todas as dependências
pip install -r requirements.txt
```

### 2. Configuração de Variáveis de Ambiente

```bash
# Copie o arquivo template
cp .env.example .env

# Edite .env com suas configurações (abra em seu editor)
# nano .env  (Linux/Mac)
# code .env  (VSCode)

# Variáveis importantes a configurar:
DATABASE_URL=sqlite:///./safeplan.db
PI_SERVER=SESAUPI01                           # PI Data Archive
AF_SERVER=SAURIOPIAF02                        # PI AF Server
AF_DATABASE=DB_BUZIOS_SENSORES                # AF Database
TEAMS_WEBHOOK_URL=https://outlook.webhook...  # Microsoft Teams (opcional)
LOG_LEVEL=INFO
```

### 3. Inicialização do Banco de Dados

```bash
# Criar schema e tabelas do banco de dados
python scripts/init_db.py

# Resultado esperado:
# ✓ Database inicializado
# ✓ Tabelas criadas: sensor_config, sensor_readings, alert_definitions, etc.
```

### 4. Opcional: Gerar Dados de Demonstração

```bash
# Criar 11 sensores de exemplo com 1.848 leituras para testes
python scripts/create_sample_data.py

# Resultado esperado:
# ✓ 11 sensores criados
# ✓ 1848 leituras criadas
# ✓ 22 definições de alertas criadas
```

### 5. Executar Testes

```bash
# Testes de Fase 1 (Data Layer)
python -m pytest tests/unit/test_data_layer.py -v

# Testes de Fase 3 (Machine Learning)
python -m pytest tests/unit/test_ml.py -v

# Executar todos os testes
python -m pytest tests/ -v
```

### 6. Integração com PI AF Server (Fase 2B)

#### Pré-requisitos:
- PI AF SDK instalado em `C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0`
- Python 3.8+ com pythonnet instalado
- Acesso à rede corporativa e SAURIOPIAF02

#### Instalação do pythonnet:
```bash
pip install pythonnet
```

#### Descobrir Sensores do AF Server:
```bash
# Modo real (conecta ao SAURIOPIAF02\DB_BUZIOS_SENSORES)
python scripts/discover_sensor_paths.py

# Modo demo (usa dados de demonstração)
python scripts/discover_sensor_paths.py --demo

# Com limite de sensores (útil para testes)
python scripts/discover_sensor_paths.py --max-results=500

# Resultado: config/sensor_paths_buzios.json será criado
```

#### Importar Sensores para SafePlan:
```bash
# Importa sensores do arquivo JSON descoberto
python scripts/import_sensors_simple.py

# Resultado esperado:
# ✓ 50-5000 sensores importados (conforme descoberta)
# ✓ Thresholds automáticos aplicados por tipo
# ✓ Regras de alerta criadas (Warning + Critical)
```

### 7. Iniciar o Dashboard

```bash
# Inicie o Streamlit (modo desenvolvimento)
streamlit run app/main.py

# Ou especifique porta e modo:
streamlit run app/main.py --server.port=8501 --server.headless=true

# Acesse no navegador:
# http://localhost:8501
```

### 8. Treinar Modelos de Machine Learning

No dashboard, vá para:
1. **Predictions** (aba na barra lateral)
2. **Training** (segunda aba)
3. Selecione os sensores
4. Clique em "Treinar Modelos"

Após treino, teste:
- **Forecasting:** Previsões de 24 horas para cada sensor
- **Anomaly Detection:** Detecção de comportamentos anômalos
- **Model Status:** Cobertura e qualidade dos modelos

---

## � Fase 3 - ML Integration (Completa ✅)

### Implementado

Integração completa de Machine Learning para detecção de anomalias e forecasting de séries temporais.

1. **Anomaly Detection** (`src/ml/anomaly_detector.py`)
   - Isolation Forest: Detecção por isolamento de pontos anômalos
   - Local Outlier Factor: Detecção por densidade local
   - Ensemble: Votação ponderada de múltiplos algoritmos
   - Scores normalizados (0-1) para confiança

2. **Time Series Forecasting** (`src/ml/forecaster.py`)
   - Facebook Prophet para forecasting automático
   - Detecção de tendências (trend) e sazonalidade (yearly/weekly)
   - Intervalos de confiança configuráveis (95% default)
   - Métricas: MAPE, RMSE, MAE

3. **ML Engine** (`src/ml/ml_engine.py`)
   - Orquistra operações: treino, detecção, forecasting
   - Gerencia múltiplos modelos por sensor
   - Persiste predições em banco de dados
   - Suporte para retrein automático

4. **ML Repositories** (`src/ml/repositories.py`)
   - PredictionRepository: CRUD de predições
   - SensorReadingsRepository: Acesso a histórico
   - ModelTrainingRepository: Gerenciamento de treino

5. **Streamlit Predictions Page** (`app/pages/predictions_page.py`)
   - **Forecasting Tab:** Visualização de forecast com intervalo de confiança
   - **Anomaly Detection Tab:** Status atual + histórico com anomalias
   - **Model Status Tab:** Cobertura de modelos, detalhes por sensor
   - **Training Tab:** Interface para treino de modelos

6. **Unit Tests** (`tests/unit/test_ml.py`)
   - 15+ testes para AnomalyDetector
   - 8+ testes para TimeSeriesForecaster
   - Testes de casos extremos (dados pequenos, valores constantes)

7. **Documentação** (`docs/PHASE3_ML_GUIDE.md`)
   - Guia completo de ML Integration (30+ páginas)
   - Exemplos de código
   - Troubleshooting
   - Performance & escalabilidade

### Requisitos de Dados

- **Anomaly Detectionriesction:** 30+ amostras (ideal: 168+)
- **Forecasting:** 50+ amostras (ideal: 500+)
- **Qualidade:** data_quality = 0 apenas

### Thresholds Automáticos (Anomaly Detection)

- "Muito Normal": score 0.0-0.3
- "Potencial Anomalia": score 0.3-0.6
- "Provável Anomalia": score 0.6-0.9
- "Certamente Anomalia": score 0.9-1.0

### Métricas de Qualidade (Forecasting)

- MAPE < 10% = Bom
- RMSE < 5 = Bom
- MAE < 3 = Bom

### Workflows

```
[1] Interface Predictions
    ├─ Forecasting: Selecionar sensor + horizonte
    ├─ Anomaly: Visualizar status + histórico
    ├─ Model Status: Ver cobertura de modelos
    └─ Training: Treinar modelos

[2] ML Engine (Código)
    ├─ engine = create_ml_engine()
    ├─ result = engine.detect_anomalies(sensor_id)
    ├─ result = engine.forecast_sensor(sensor_id, periods=24)
    ├─ engine.train_anomaly_detector(sensor_id)
    └─ status = engine.retrain_all_models()

[3] Integração com Alerts
    ├─ Anomaly Detection → Alertas automáticos
    └─ Forecasting → Alertas proativos
```

---

## 📅 Próximas Fases

- **Fase 4:** Advanced UI & Reporting (Dashboards, PDF/Excel)
- **Fase 5:** Scheduling & Automation (Retrein automático)
- **Fase 6:** Deployment & Hardening (Production ready)

## 📚 Documentação

- **Fase 1 Guide:** `docs/ARCHITECTURE.md`
- **Fase 2 Guide:** `docs/PHASE2_GUIDE.md`
- **Fase 2B Guide:** `docs/PI_AF_INTEGRATION.md`
- **Fase 3 Guide:** `docs/PHASE3_ML_GUIDE.md`
- **Database Schema:** `docs/DATABASE_SCHEMA.md`
- **Plano Detalhado:** Ver arquivo de plano

---

**Status:** Fase 3 (ML Integration) ✅
**Próximo:** Fase 4 (Advanced UI & Reporting)