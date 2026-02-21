# SafePlan - Fase 3: ML Integration (Machine Learning)

> Integração de Machine Learning para detecção de anomalias e forecasting de séries temporais

**Status:** ✅ Implementado

**Última Atualização:** 2026-02-20

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Componentes Implementados](#componentes-implementados)
3. [Anomaly Detection](#anomaly-detection)
4. [Time Series Forecasting](#time-series-forecasting)
5. [ML Engine](#ml-engine)
6. [Interface Streamlit](#interface-streamlit)
7. [Uso e Exemplos](#uso-e-exemplos)
8. [Testes](#testes)
9. [Troubleshooting](#troubleshooting)

---

## 📊 Visão Geral

A Fase 3 introduz capacidades de Machine Learning ao SafePlan:

### **Anomaly Detection** 🚨
- Detecta comportamentos anormais em leituras de sensores
- Usa ensemble de algoritmos: Isolation Forest + Local Outlier Factor
- Scores de anomalia normalizados (0-1)

### **Time Series Forecasting** 🔮
- Prevê valores futuros de sensores
- Baseado em Facebook Prophet
- Intervalos de confiança configuráveis
- Detecção automática de tendências e sazonalidade

### **ML Engine** 🔧
- Orquestra operações de ML
- Gerencia múltiplos modelos por sensor
- Persiste predições em banco de dados
- Monitoramento de qualidade dos modelos

---

## 📦 Componentes Implementados

### Backend

#### 1. **Anomaly Detector** (`src/ml/anomaly_detector.py`)

Detecta anomalias usando dois algoritmos:

**Isolation Forest**
- Isola pontos anômalos partir de isolamento
- Eficiente para dados altos-dimensionais
- Rápido para detecção online

**Local Outlier Factor (LOF)**
- Detecta anomalias com base em densidade local
- Melhor para agrupamentos não esféricos
- Sensível a mudanças de densidade

**Ensemble**
- Combina ambos algoritmos com votação ponderada
- Threshold de confiança configurável (default: 0.5)
- Score final normalizado (0-1)

```python
from src.ml.anomaly_detector import create_anomaly_detector

detector = create_anomaly_detector(contamination=0.1)
detector.fit(historical_data)

predictions, scores = detector.detect_ensemble(new_data)
summary = detector.get_anomaly_summary(data)
```

**Métodos Principais:**
- `fit(data)` - Treina o detector
- `detect_isolation_forest(data)` - Detecção IS
- `detect_lof(data)` - Detecção LOF
- `detect_ensemble(data, threshold)` - Detecção ensemble
- `calculate_anomaly_threshold(data, percentile)` - Calcula threshold adaptativo
- `get_anomaly_summary(data)` - Resumo estatístico

**Parâmetros:**
- `contamination` (float): Taxa esperada de anomalias (0.01 a 0.5)
- `threshold` (float): Threshold de confiança ensemble (0.3 a 0.8)

---

#### 2. **Time Series Forecaster** (`src/ml/forecaster.py`)

Previsões baseadas em Facebook Prophet

**Características:**
- Detecção automática de tendências
- Sazonalidade anual/semanal/diária
- Changepoints automáticos (mudanças de tendência)
- Intervalos de confiança ajustáveis

```python
from src.ml.forecaster import create_forecaster

forecaster = create_forecaster(interval_width=0.95)
forecaster.fit(timestamps, values)

forecast = forecaster.forecast(periods=24)  # Próximas 24 horas
metrics = forecaster.calculate_metrics()
summary = forecaster.forecast_summary()
```

**Métodos Principais:**
- `fit(timestamps, values)` - Treina o modelo
- `forecast(periods)` - Forecast de N períodos
- `forecast_with_history(periods)` - Forecast + histórico
- `calculate_metrics()` - MAPE, RMSE, MAE
- `forecast_summary(periods)` - Resumo da previsão
- `get_components()` - Componentes do modelo

**Retorno do forecast:**
```python
{
    'timestamps': [datetime, ...],          # Timestamps previstos
    'forecasted_values': [float, ...],      # Valores previstos
    'lower_bound': [float, ...],            # Limite inferior (95%)
    'upper_bound': [float, ...],            # Limite superior (95%)
    'trend': [float, ...]                   # Componente de tendência
}
```

**Métricas:**
- **MAPE** (Mean Absolute Percentage Error): Erro percentual médio
- **RMSE** (Root Mean Square Error): Raiz do erro quadrático médio
- **MAE** (Mean Absolute Error): Erro absoluto médio

> Lower is better for all metrics

---

#### 3. **ML Engine** (`src/ml/ml_engine.py`)

Orquestrador central de operações ML

```python
from src.ml.ml_engine import create_ml_engine

engine = create_ml_engine()

# Detecção de anomalias
anomaly_result = engine.detect_anomalies(sensor_id=1)
# {
#     'is_anomaly': bool,
#     'anomaly_score': float (0-1),
#     'value': float,
#     'historical_average': float,
#     'historical_std': float
# }

# Forecasting
forecast_result = engine.forecast_sensor(sensor_id=1, periods=24)
# {
#     'forecast': {...},
#     'metrics': {...},
#     'summary': {...}
# }

# Treino de modelos
engine.train_anomaly_detector(sensor_id=1, hours=168, contamination=0.1)
engine.train_forecaster(sensor_id=1, hours=72)

# Retrein todos os modelos
status = engine.retrain_all_models()

# Status dos modelos
status = engine.get_ml_status()
```

**Métodos Principais:**
- `get_sensor_history(sensor_id, hours)` - Recupera histórico
- `train_anomaly_detector(sensor_id, hours, contamination)` - Treina AD
- `train_forecaster(sensor_id, hours)` - Treina forecaster
- `detect_anomalies(sensor_id)` - Detecta anomalias atuais
- `forecast_sensor(sensor_id, periods)` - Realiza forecast
- `save_prediction(...)` - Salva no DB
- `get_predictions(sensor_id, model_type, limit)` - Recupera predições
- `retrain_all_models()` - Retreina todos
- `get_ml_status()` - Status global

---

#### 4. **ML Repositories** (`src/ml/repositories.py`)

Camada de abstração para dados

**PredictionRepository**
- Operações CRUD em predições
- Busca por sensor, recentes, anomalias
- Estatísticas de predições
- Limpeza de dados antigos

**SensorReadingsRepository**
- Acesso a leituras históricas
- Cálculo de estatísticas
- Filtros por qualidade

**ModelTrainingRepository**
- Identifica sensores treináveis
- Verifica requisitos de dados

---

### Frontend

#### **Predictions Page** (`app/pages/predictions_page.py`)

Interface Streamlit com 4 abas:

##### 1. **Forecasting** 🔮
- Seleção de sensor e horizonte
- Visualização de forecast com intervalo de confiança
- Métricas de qualidade (MAPE, RMSE, MAE)
- Resumo da previsão (tendência, volatilidade)

##### 2. **Anomaly Detection** 🚨
- Seleção de sensor
- Status atual (Normal/Anomalia)
- Score de anomalia
- Gráfico histórico com anomalias destacadas
- Linhas de referência (média, desvio padrão)

##### 3. **Model Status** 🔧
- Cobertura de modelos treinados
- Detalhes por sensor:
  - Sensor name
  - Plataforma
  - Tipo
  - Status do anomaly detector
  - Status do forecaster

##### 4. **Training** 🎯
- Seleção de sensores para treino
- Botão de treino com progresso
- Requisitos de dados
- Dicas de melhoria

---

## 🚨 Anomaly Detection

### Como Funciona

1. **Treino (Off-line)**
   - Coleta dados históricos (72 horas padrão)
   - Treina Isolation Forest + LOF com dados limpos
   - Calcula scores de normalidade

2. **Detecção (Online)**
   - Novos dados são passados para ambos modelos
   - Cada modelo gera predição (-1=anomalia, 1=normal)
   - Scores são normalizados e combinados
   - Resultado final: predição + score (0-1)

### Interpretação de Scores

| Score | Interpretação | Ação |
|-------|---------------|------|
| 0.0-0.3 | Muito Normal | Nenhuma |
| 0.3-0.6 | Potencial Anomalia | Investigar |
| 0.6-0.9 | Provável Anomalia | Alerta |
| 0.9-1.0 | Certamente Anomalia | Crítico |

### Requisitos de Dados

- **Mínimo:** 30 amostras
- **Ideal:** 168+ amostras (7 dias)
- **Qualidade:** data_quality = 0 apenas

### Configuração

```python
detector = create_anomaly_detector(contamination=0.1)
```

**Contamination:** Taxa esperada de anomalias
- 0.05 = 5% esperado como anomalia
- 0.10 = 10% esperado como anomalia
- Usar valores baixos (0.05-0.15) em geral

### Exemplo

```python
from src.ml.ml_engine import create_ml_engine

engine = create_ml_engine()

# Detectar anomalias
result = engine.detect_anomalies(sensor_id=1)

if result['is_anomaly']:
    print(f"🚨 ANOMALIA DETECTADA!")
    print(f"Score: {result['anomaly_score']:.4f}")
    print(f"Valor: {result['value']:.2f}")
    print(f"Média Histórica: {result['historical_average']:.2f}")
```

---

## 🔮 Time Series Forecasting

### Como Funciona

1. **Preparação**
   - Séries temporais são convertidas para formato Prophet
   - Duplicatas são removidas
   - Dados são ordenados por timestamp

2. **Treino**
   - Prophet treina modelo com detecção automática de:
     - Tendências (trend)
     - Sazonalidade anual (yearly)
     - Sazonalidade semanal (weekly)
     - Changepoints (mudanças abruptas)

3. **Forecast**
   - Propaga componentes para futuro
   - Gera intervalos de confiança (95% padrão)
   - Retorna trend e forecasted values

4. **Métricas**
   - Validação cruzada nos últimos 10% dos dados
   - Calcula MAPE, RMSE, MAE

### Interpretação de Métricas

| Métrica | Boa | Aceitável | Ruim |
|---------|-----|-----------|------|
| MAPE | < 10% | 10-20% | > 20% |
| RMSE | < 5 | 5-15 | > 15 |
| MAE | < 3 | 3-10 | > 10 |

> Valores dependem da escala dos dados

### Requisitos de Dados

- **Mínimo:** 50 amostras
- **Ideal:** 500+ amostras (para sazonalidade)
- **Frequência:** Preferir dados regularmente espaçados
- **Qualidade:** data_quality = 0 apenas

### Configuração

```python
forecaster = create_forecaster(
    interval_width=0.95,           # 95% confidence
    yearly_seasonality=True,        # Sazonalidade anual
    weekly_seasonality=True,        # Sazonalidade semanal
    daily_seasonality=False         # Sazonalidade diária
)
```

### Exemplo

```python
from src.ml.ml_engine import create_ml_engine

engine = create_ml_engine()

# Forecast para 24 horas
result = engine.forecast_sensor(sensor_id=1, periods=24)

forecast = result['forecast']
metrics = result['metrics']
summary = result['summary']

print(f"Tendência: {summary['trend_direction']}")
print(f"Volatilidade: {summary['volatility']:.2f}")
print(f"MAPE: {metrics['mape']:.2f}%")
print(f"RMSE: {metrics['rmse']:.4f}")
```

---

## 🔧 ML Engine

### Fluxo de Operação

```
┌─────────────────────────────────────────────┐
│           ML Engine Start                   │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
    Anomaly          Forecast
    Detector         Timeseries
         │               │
         ├───────┬───────┤
         │       │       │
    ┌────┴──┐ ┌──┴──┐ ┌──┴──┐
    │ Train │ │Test │ │Save │
    └────┬──┘ └──┬──┘ └──┬──┘
         │       │       │
         └───────┴───────┘
              │
         ┌────▼─────┐
         │  Results │
         └──────────┘
```

### Lifecycle de um Modelo

1. **Treino** (Training)
   - Coleta dados históricos
   - Treina modelo
   - Persiste em memória (não em arquivo)

2. **Inferência** (Inference)
   - Recebe novos dados
   - Aplica modelo
   - Retorna predições

3. **Validação** (Validation)
   - Valida qualidade via métricas
   - Monitora performance

4. **Retreino** (Retraining)
   - Periodicamente (daily/weekly)
   - Usa novos dados coletados
   - Atualiza modelos

### Persistência de Predições

As predições são salvas em `ml_predictions` :

```python
engine.save_prediction(
    sensor_id=1,
    model_type='FORECASTER',
    prediction_timestamp=datetime.now(),
    forecasted_value=55.2,
    confidence_low=51.0,
    confidence_high=59.4,
)
```

### Recuperação de Predições

```python
predictions = engine.get_predictions(
    sensor_id=1,
    model_type='FORECASTER',
    limit=100
)
```

---

## 💻 Interface Streamlit

### Acessar

1. Abrir Dashboard: `streamlit run app/main.py`
2. Navegar para: **Predictions**

### Workflows

#### Workflow 1: Visualizar Forecast

```
1. Ir para "Forecasting" tab
2. Selecionar sensor
3. Ajustar horizonte (hours)
4. Visualizar chart com intervalo de confiança
5. Verificar métricas (MAPE, RMSE, MAE)
```

#### Workflow 2: Detectar Anomalias

```
1. Ir para "Anomaly Detection" tab
2. Selecionar sensor
3. Ver status (Normal/Anomalia)
4. Ver score de anomalia
5. Ver histórico com anomalias destacadas
```

#### Workflow 3: Treinar Modelos

```
1. Ir para "Training" tab
2. Selecionar sensores
3. Clicar "Treinar Modelos"
4. Aguardar progresso
5. Ver resultado (quantos treinados)
```

#### Workflow 4: Monitorar Status

```
1. Ir para "Model Status" tab
2. Ver cobertura global
3. Ver detalhes por sensor
4. Identificar sensors sem modelos
```

---

## 🎯 Uso e Exemplos

### Exemplo 1: Monitorar Anomalias em Tempo Real

```python
from src.ml.ml_engine import create_ml_engine
from src.sensors.sensor_manager import create_sensor_manager
import time

engine = create_ml_engine()
sensor_mgr = create_sensor_manager()

sensors = sensor_mgr.get_enabled_sensors()

while True:
    for sensor in sensors:
        result = engine.detect_anomalies(sensor.sensor_id)
        
        if result.get('is_anomaly'):
            print(f"⚠️ Anomalia em {sensor.display_name}")
            print(f"   Score: {result['anomaly_score']:.4f}")
            
            # Salvar predição
            engine.save_prediction(
                sensor_id=sensor.sensor_id,
                model_type='ANOMALY_DETECTOR',
                prediction_timestamp=result['timestamp'],
                anomaly_score=result['anomaly_score'],
                is_anomaly=True
            )
    
    time.sleep(60)  # Verificar a cada minuto
```

### Exemplo 2: Forecasting com Alertas

```python
from src.ml.ml_engine import create_ml_engine
from src.alerting.alert_engine import create_alert_engine

ml_engine = create_ml_engine()
alert_engine = create_alert_engine()

# Forecast para próximas 24 horas
result = ml_engine.forecast_sensor(sensor_id=1, periods=24)
forecast = result['forecast']

# Verificar se forecast ultrapassa limites
max_forecasted = max(forecast['forecasted_values'])
threshold = 100.0

if max_forecasted > threshold:
    print(f"⚠️ Forecast prevê ultrapassar {threshold}")
    print(f"   Máximo: {max_forecasted:.2f}")
    
    # Criar alerta proativo
    alert_engine.create_alert(
        sensor_id=1,
        severity_level=2,  # Warning
        notes=f"Forecast: {max_forecasted:.2f} > {threshold}"
    )
```

### Exemplo 3: Retrein Automático

```python
from src.ml.ml_engine import create_ml_engine
from apscheduler.schedulers.background import BackgroundScheduler

engine = create_ml_engine()

def retrain_daily():
    """Retreina todos os modelos diariamente"""
    print("🔄 Iniciando retrein...")
    result = engine.retrain_all_models()
    print(f"✓ Retrein concluído: {result}")

# Agendar para todos os dias às 02:00 AM
scheduler = BackgroundScheduler()
scheduler.add_job(
    retrain_daily,
    'cron',
    hour=2,
    minute=0
)
scheduler.start()
```

---

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes ML
python -m pytest tests/unit/test_ml.py -v

# Teste específico
python -m pytest tests/unit/test_ml.py::TestAnomalyDetector::test_isolation_forest_detection -v

# Com cobertura
python -m pytest tests/unit/test_ml.py --cov=src/ml --cov-report=html
```

### Cobertura de Testes

| Componente | Cobertura | Status |
|------------|-----------|--------|
| AnomalyDetector | 90%+ | ✓ |
| TimeSeriesForecaster | 85%+ | ✓ |
| MLEngine | 80%+ | ✓ |

### Casos Testados

**AnomalyDetector:**
- Inicialização
- Treino
- Detecção (IF, LOF, Ensemble)
- Calque de threshold
- Resumos
- Casos extremos (dados pequenos, valores constantes)

**TimeSeriesForecaster:**
- Inicialização
- Preparação de dados
- Treino
- Forecast
- Métricas
- Forecast com histórico

### Exemplo de Teste

```python
import pytest
from src.ml.anomaly_detector import create_anomaly_detector
import numpy as np

def test_anomaly_detection():
    # Setup
    detector = create_anomaly_detector(contamination=0.1)
    data = np.random.normal(50, 5, 100)
    
    # Execute
    detector.fit(data)
    predictions, scores = detector.detect_ensemble(data)
    
    # Assert
    assert len(predictions) == len(data)
    assert all(p in [-1, 1] for p in predictions)
```

---

## 📊 Integração com Alert Engine

Os resultados de ML podem disparar alertas:

### Anomaly Detection → Alerts

```python
# No alerting engine
if anomaly_result['is_anomaly'] and anomaly_result['anomaly_score'] > 0.8:
    alert_engine.create_alert(
        sensor_id=sensor_id,
        severity_level=3,  # Danger
        alert_type='ANOMALY',
        notes=f"Anomaly score: {anomaly_result['anomaly_score']:.4f}"
    )
```

### Forecasting → Proactive Alerts

```python
# Alerta proativo antes de limite ser atingido
forecast_data = ml_engine.forecast_sensor(sensor_id, periods=24)
max_forecast = max(forecast_data['forecast']['forecasted_values'])

if max_forecast > upper_critical_limit:
    alert_engine.create_alert(
        sensor_id=sensor_id,
        severity_level=4,  # Critical
        alert_type='FORECAST_WARNING',
        notes=f"Forecast predicts critical level: {max_forecast:.2f}"
    )
```

---

## 🐛 Troubleshooting

### Problema: "Dados insuficientes"

**Causa:** Menos de 30 amostras para anomaly detector ou 50 para forecaster

**Solução:**
1. Verificar sensor está coletando dados
2. Aguardar mais dados serem coletados
3. Verificar data_quality dos dados (deve ser 0)

```sql
-- Verificar dados
SELECT COUNT(*), data_quality 
FROM sensor_readings 
WHERE sensor_id = 1 
GROUP BY data_quality;
```

### Problema: MAPE/RMSE muito alto

**Causa:** Dados com muita variabilidade ou modelos não treinados adequadamente

**Solução:**
1. Coletar mais dados históricos
2. Verificar se há mudanças abruptas (changepoints)
3. Retreinar modelo

### Problema: Muitas falsos-positivos em anomalias

**Causa:** Contamination rate muito alto ou dados ruim

**Solução:**
```python
# Reduzir contamination
detector = create_anomaly_detector(contamination=0.05)

# Ou usar threshold maior
predictions, scores = detector.detect_ensemble(
    data,
    threshold=0.7  # Aumentar de 0.5
)
```

### Problema: Modelos não persistem

**Causa:** Modelos são armazenados em memória, perdidos ao restart

**Solução:**
Treinar novamente após restart:
```python
engine.retrain_all_models()
```

Ou agendador para retrein automático diário.

### Problema: Memory leak

**Causa:** Muitos sensores com modelos pesados

**Solução:**
1. Limitar numero de sensores
2. Fazer cleanup periodicamente
3. Usar garbage collection

```python
import gc
engine.retrain_all_models()
gc.collect()  # Limpar memória
```

---

## 📈 Performance & Escalabilidade

### Benchmark (Laptop típico)

| Operação | Tempo | Sensores |
|----------|-------|----------|
| Treinar AD | 500ms | 100 |
| Detectar anomalia | 10ms | Instant |
| Treinar Forecaster | 2s | 100 |
| Fazer forecast | 50ms | Instant |
| Retrein todos (100 sensors) | 3min | Automático |

### Otimizações

1. **Cache de modelos** em memória
2. **Lazy loading** de dados históricos
3. **Batch processing** para múltiplos sensores
4. **Índices no banco de dados** para sensor_id, timestamps

### Escalabilidade

- **Atual:** 100-500 sens em laptop
- **Otimizado:** 1000+ sensores em servidor
- **Enterprise:** Usar PostgreSQL + Redis cache

---

## 🚀 Próximos Passos

### Fase 4 (Advanced UI & Reporting)
- Dashboard em tempo real com WebSockets
- Relatórios PDF/Excel com predições
- Export de modelos para deployment

### Fase 5 (Scheduling & Automation)
- Scheduler para retrein automático (daily)
- Alertas automáticos baseados em forecasts
- Integração com alertas do Teams

### Futuro
- MLOps (Model versioning, experiment tracking)
- AutoML para otimização de hyperparameters
- Deep Learning (LSTM, Transformer) para séries longas
- Detecção de drift de dados

---

## 📚 Referências

- [Prophet Documentation](https://facebook.github.io/prophet/)
- [Scikit-learn Anomaly Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [Isolation Forest Paper](https://ieeexplore.ieee.org/document/5356536)
- [Local Outlier Factor](https://en.wikipedia.org/wiki/Local_outlier_factor)

---

**Contato:** Gabriel Motta (info.motta@gmail.com)

**Licença:** Proprietary - Petrobras

---

*Documentação atualizada em: 2026-02-20 16:00 UTC*
