# SafePlan - Fase 2: Core Alerting

## 🎯 Objetivo

Implementar o core de alertas com:
- Alert Engine (state machine)
- Threshold-based alerting
- Teams webhook integration
- Streamlit dashboard básico
- Sensor configuration UI

## ✅ Implementado

### Core Components

#### 1. **Alert Engine** (`src/alerting/alert_engine.py`)

State machine para gerenciar ciclo de vida de alertas:

```
NEW → ACTIVE → ACKNOWLEDGED/RESOLVED
```

**Funcionalidades:**
- Avalia sensor values contra definições de alerta
- THRESHOLD checking: valor > threshold_value
- ANOMALY checking: anomaly_score > threshold
- FORECAST checking: tendências perigosas
- State transitions automáticas
- Deduplicação de alertas

**API Principal:**
```python
from src.alerting.alert_engine import create_alert_engine

engine = create_alert_engine()

# Trigger alerts based on reading
alerts = engine.evaluate_and_trigger(
    sensor_id=1,
    current_value=120.0,  # ppm
    alert_definitions=alert_defs,
    anomaly_score=0.85,
    forecast_value=150.0
)

# Get active alerts
active = engine.get_active_alerts()

# Acknowledge/Resolve
engine.acknowledge_alert(alert_id)
engine.resolve_alert(alert_id)

# Statistics
stats = engine.get_alert_statistics()
```

---

#### 2. **Teams Notifier** (`src/alerting/teams_notifier.py`)

Integração com Microsoft Teams via Incoming Webhook.

**Funcionalidades:**
- Adaptive Cards formatadas
- Retry logic com exponential backoff
- Webhook connectivity testing
- Notification logging
- Support para múltiplas severidades

**API Principal:**
```python
from src.alerting.teams_notifier import create_teams_notifier

notifier = create_teams_notifier()

# Send alert notification
success = notifier.notify_alert(alert)

# Test webhook
if TeamsNotifier.test_webhook(webhook_url):
    print("Webhook OK")

# Batch notify critical alerts
count = notifier.notify_critical_alerts()
```

**Configuração:**
```env
TEAMS_WEBHOOK_URL=https://outlook.webhook.office.com/webhookb2/...
ALERT_RETRY_MAX_ATTEMPTS=3
ALERT_RETRY_BACKOFF_SECONDS=5
```

---

#### 3. **Sensor Manager** (`src/sensors/sensor_manager.py`)

Gerencia configuração e ciclo de vida de sensores.

**Funcionalidades:**
- CRUD operations para sensores
- Threshold management
- Alert rule creation
- Sensor status queries
- Platform/type filtering

**API Principal:**
```python
from src.sensors.sensor_manager import create_sensor_manager

mgr = create_sensor_manager()

# Create sensor
sensor = mgr.create_sensor(
    internal_name='CH4_P74_01',
    display_name='CH4 Platform 74',
    sensor_type='CH4_POINT',
    platform='P74',
    unit='ppm',
    pi_server_tag='P74_CH4_01',
    upper_critical_limit=100.0
)

# Get sensors
all = mgr.get_all_sensors()
enabled = mgr.get_enabled_sensors()
p74_sensors = mgr.get_platform_sensors('P74')

# Create alert rule
rule = mgr.create_alert_rule(
    sensor_id=sensor.sensor_id,
    condition_type='THRESHOLD',
    severity_level=4,
    threshold_value=100.0
)

# Sensor status
status = mgr.get_sensor_status(sensor.sensor_id)

# Disable/Enable
mgr.disable_sensor(sensor_id)
mgr.enable_sensor(sensor_id)
```

---

#### 4. **Streamlit Application** (`app/main.py`)

Multi-page dashboard com interface intuitiva.

**Pages:**
1. **Dashboard**: Real-time monitoring com métricas por plataforma
2. **Alerts**: Active alerts com ações (acknowledge/resolve)
3. **Predictions**: Placeholder para Phase 3 (ML)
4. **Configuration**: Sensor management UI
5. **Reports**: Placeholder para Phase 4
6. **DevTools**: Debug tools e status

**Features:**
- Auto-refresh (20-30s)
- Responsive layout com Streamlit
- Session state management
- Error handling e logging
- Configuration display

---

### Database Schema (Updated)

Nenhuma nova tabela, mas relacionamentos são agora utilizados:

```
SensorConfig → SensorReading
SensorConfig → AlertDefinition
AlertDefinition → AlertHistory
AlertHistory → NotificationLog
```

---

### Data Models (Updated)

Novos enums para Type Safety:

```python
class AlertStatus(Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"

class AlertSeverity(Enum):
    OK = 1
    WARNING = 2
    DANGER = 3
    CRITICAL = 4

class AlertCondition(Enum):
    THRESHOLD = "THRESHOLD"
    ANOMALY = "ANOMALY"
    FORECAST = "FORECAST"
```

---

## 🚀 Como Usar

### 1. Setup

```bash
# Clone e setup
cd SafePlan
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with your credentials
```

### 2. Initialize Database

```bash
python scripts/init_db.py
```

### 3. Run Integration Tests

```bash
python scripts/test_phase2.py
```

Expected output:
```
======================================================================
  TEST 1: Database Connection & Initialization
======================================================================
✓ Database configured: sqlite:///./safeplan.db
✓ Database connection OK

======================================================================
  TEST 2: Sensor Management
======================================================================
✓ Created sensor: CH4_P74_01
✓ Created sensor: H2S_P75_01
✓ Retrieved 2 sensors from database
...
```

### 4. Start Streamlit Dashboard

```bash
streamlit run app/main.py
```

Default: http://localhost:8501

---

## 📊 Usage Examples

### Example 1: Create Sensor with Alerts

```python
from src.sensors.sensor_manager import create_sensor_manager
from src.alerting.alert_engine import create_alert_engine

sensor_mgr = create_sensor_manager()

# Create sensor
sensor = sensor_mgr.create_sensor(
    internal_name='CH4_P74_01',
    display_name='CH4 Platform 74 - Sensor 01',
    sensor_type='CH4_POINT',
    platform='P74',
    unit='ppm',
    pi_server_tag='P74_CH4_01',
    lower_warning_limit=5.0,
    upper_warning_limit=50.0,
    upper_critical_limit=100.0
)

# Create alert rules
sensor_mgr.create_alert_rule(
    sensor_id=sensor.sensor_id,
    condition_type='THRESHOLD',
    severity_level=3,  # DANGER
    threshold_value=50.0
)

sensor_mgr.create_alert_rule(
    sensor_id=sensor.sensor_id,
    condition_type='THRESHOLD',
    severity_level=4,  # CRITICAL
    threshold_value=100.0
)
```

### Example 2: Simulate Alerts

```python
from src.alerting.alert_engine import create_alert_engine
from src.sensors.sensor_manager import create_sensor_manager

alert_engine = create_alert_engine()
sensor_mgr = create_sensor_manager()

sensor = sensor_mgr.get_sensor(1)
rules = sensor_mgr.get_alert_rules(sensor.sensor_id)

# Normal value - no alert
alerts = alert_engine.evaluate_and_trigger(
    sensor_id=sensor.sensor_id,
    current_value=40.0,
    alert_definitions=rules
)
print(f"Alerts: {len(alerts)}")  # Output: 0

# Critical value - triggers alert
alerts = alert_engine.evaluate_and_trigger(
    sensor_id=sensor.sensor_id,
    current_value=120.0,
    alert_definitions=rules
)
print(f"Alerts: {len(alerts)}")  # Output: 1

alert = alerts[0]
print(f"Status: {alert.status}")  # ACTIVE
print(f"Severity: {alert.severity_level}")  # 4 (CRITICAL)
```

### Example 3: Teams Notifications

```python
from src.alerting.teams_notifier import TeamsNotifier

notifier = TeamsNotifier()

# Test webhook
if TeamsNotifier.test_webhook(webhook_url):
    print("✓ Webhook accessible")

# Send notification for alert
success = notifier.notify_alert(alert)
```

---

## 🔧 Configuração Avançada

### Alert Rules por Tipo

```python
# THRESHOLD: Valor excede limite
sensor_mgr.create_alert_rule(
    sensor_id=sensor_id,
    condition_type='THRESHOLD',
    severity_level=4,
    threshold_value=100.0
)

# ANOMALY: Comportamento anormal detectado
sensor_mgr.create_alert_rule(
    sensor_id=sensor_id,
    condition_type='ANOMALY',
    severity_level=3,
    anomaly_threshold=0.7  # 0-1 scale
)

# FORECAST: Previsão indica tendência perigosa
sensor_mgr.create_alert_rule(
    sensor_id=sensor_id,
    condition_type='FORECAST',
    severity_level=3,
    threshold_value=90.0
)
```

### Retry Policy

```env
# Retry configuration
ALERT_RETRY_MAX_ATTEMPTS=3
ALERT_RETRY_BACKOFF_SECONDS=5
# Backoff: 5s, 10s, 20s (exponential)
```

---

## 📈 Performance Characteristics

- **Database Queries**: Otimizadas com índices
- **Alert Evaluation**: O(n) onde n = número de alert definitions
- **Streamlit Re-renders**: ~1-2s por página
- **Teams API Calls**: ~2-3s timeout + retry logic

---

## 🧪 Testes

### Unit Tests (Fase 1)

```bash
python -m pytest tests/unit/test_data_layer.py -v
```

### Integration Tests (Fase 2)

```bash
python scripts/test_phase2.py
```

### Manual Testing

1. Start app: `streamlit run app/main.py`
2. Add sensor via Configuration tab
3. Create alert rule
4. Simulate value via script or DB
5. Verify alert appears in Alerts page
6. Acknowledge/Resolve alert

---

## 🚨 Troubleshooting

### Teams Webhook Not Working

```python
from src.alerting.teams_notifier import TeamsNotifier

# Test connection
if TeamsNotifier.test_webhook(webhook_url):
    print("✓ OK")
else:
    print("✗ Check URL and internet")
```

### Alerts Not Triggering

1. Verify sensor has alert rules: `sensor_mgr.get_alert_rules(sensor_id)`
2. Check threshold values match sensor reading
3. Verify alert definitions are enabled
4. Check logs: `tail -f logs/safeplan.log`

### Streamlit App Crashes

1. Restart: `streamlit run app/main.py --logger.level=debug`
2. Check database: `python scripts/init_db.py`
3. Clear cache: `rm -rf ~/.streamlit/cache`

---

## 📝 Next Steps (Fase 3)

- ML Model Integration (Anomaly Detection + Forecasting)
- ML Predictions Page
- Scheduler/Background Tasks
- Data refresh automation
- Report generation

---

## 📚 References

- Alert Engine: `src/alerting/alert_engine.py`
- Teams Notifier: `src/alerting/teams_notifier.py`
- Sensor Manager: `src/sensors/sensor_manager.py`
- Streamlit App: `app/main.py`
- Test Script: `scripts/test_phase2.py`

---

**Status:** Fase 2 (Core Alerting) ✅ Completa
**Próximo:** Fase 3 (ML Integration)
