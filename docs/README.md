# SafePlan - Documentação Central

**Índice de Documentação do Projeto**

---

## 📊 Avaliação e Planejamento Estratégico

### **1. EXECUTIVE_SUMMARY.md** 🎯
- **Público:** Liderança / Stakeholders
- **Objetivo:** Decisão estratégica sobre escalabilidade
- **Tempo leitura:** 5 minutos
- **Conteúdo:**
  - Problema do Streamlit em escala 15.000+ sensores
  - Recomendação: React + FastAPI
  - Timeline e custo
  - Comparação com alternativas

👉 **COMECE AQUI** se você é executivo ou gestor

---

### **2. FRAMEWORK_ANALYSIS.md** 📈
- **Público:** Arquitetos / Tech Leads
- **Objetivo:** Análise técnica comparativa
- **Tempo leitura:** 15 minutos
- **Conteúdo:**
  - Streamlit: vantagens, limitações, recomendação
  - Dash: comparação com Streamlit
  - React + FastAPI: arquitetura proposta ⭐
  - Grafana: monitoramento complementar
  - Tabelas de performance (9.964 vs 15.000 sensores)
  - Checklist de migração

👉 **LEIA ISTO** se você precisa entender por que mudamos

---

### **3. MIGRATION_ROADMAP.md** 🚀
- **Público:** Arquitetos / Engineering Managers
- **Objetivo:** Plano de execução fase-por-fase
- **Tempo leitura:** 20 minutos
- **Conteúdo:**
  - Contexto atual (9.964 sensores em Streamlit)
  - Arquitetura proposta (diagrama)
  - **Fase 1-5: Preparação → Backend → Frontend → Testes → Produção**
  - Timeline: 11 semanas
  - Recursos necessários (8 pessoas)
  - Riscos e mitigação
  - Critérios de sucesso

👉 **USE ISTO** para planejar a implementação

---

## 🏗️ Desenvolvimento e Arquitetura

### **4. PHASE3_IMPLEMENTATION_SUMMARY.md**
- Implementação atual das páginas Streamlit
- Modelo de dados (SensorConfig, Readings)
- Estrutura de frontend (monitoring_page, sensor_detail_page)

### **5. PI_AF_INTEGRATION.md**
- Integração com servidor PI (OSIsoft)
- Descoberta de sensores em tempo real
- Sincronização de dados

### **6. PHASE3_ML_GUIDE.md**
- Detecção de anomalias com ML
- Forecasting de leituras
- Integração com alertas

---

## 📋 Regras e Padrões

### **7. BOT_RULES.md** ✅
- **Localização alternativa:** `.claude/rules/BOT_RULES.md`
- **Público:** Developers (via Copilot/Claude)
- **Objetivo:** Consistência de código
- **Conteúdo:**
  - 8 Regras de governança de código
  - Exemplos corretos/incorretos
  - Convenções Python (snake_case, PascalCase)
  - Estrutura de pastas obrigatória
  - Segurança (credenciais em .env)
  - Checklist pré-commit

👉 **REFERENCIE ISTO** ao gerar novo código

---

## 🚀 Quick Start Guides

### **8. QUICK_START_PHASE3.txt**
- Instruções rápidas para rodar o projeto
- Dependências (requirements.txt)
- Inicializar banco de dados
- Comandos básicos (Streamlit, scripts)

### **9. PHASE2_GUIDE.md**
- Histórico de Fase 2
- Implementações completadas

---

## 🔍 Estrutura do Projeto

```
SafePlan/
├── app/                          # Frontend Streamlit (atual)
│   ├── main.py
│   ├── pages/
│   │   ├── monitoring_page.py
│   │   ├── predictions_page.py
│   │   └── sensor_detail_page.py
│   └── __init__.py
├── src/                          # Backend Python
│   ├── data/                     # ORM + Database
│   │   ├── models.py             # SensorConfig, Readings
│   │   ├── repositories.py       # Data access layer
│   │   ├── database.py           # SQLAlchemy config
│   │   └── __init__.py
│   ├── ml/                       # Machine learning
│   │   ├── anomaly_detector.py
│   │   ├── forecaster.py
│   │   └── ml_engine.py
│   ├── pi_server/                # Integração OSIsoft PI
│   │   ├── af_manager.py
│   │   ├── data_fetcher.py
│   │   └── pi_client.py
│   ├── sensors/                  # Lógica de sensores
│   │   └── sensor_manager.py
│   ├── alerting/                 # Sistema de alertas
│   │   ├── alert_engine.py
│   │   └── teams_notifier.py
│   ├── utils/
│   └── __init__.py
├── scripts/                      # Utilitários e scripts
│   ├── discover_sensors_from_af.py  # Descobrir sensores
│   ├── import_sensors_from_buzios.py # Importar para DB
│   ├── init_db.py                   # Inicializar banco
│   └── ...
├── config/                       # Configurações
│   ├── settings.py
│   ├── config_gideaopi.json
│   └── sensor_paths_buzios.json
├── tests/                        # Testes automatizados
│   ├── unit/
│   │   ├── test_data_layer.py
│   │   ├── test_ml.py
│   │   └── ...
│   └── integration/
├── docs/                         # Documentação (VOCÊ ESTÁ AQUI)
│   ├── README.md                 # Este arquivo
│   ├── EXECUTIVE_SUMMARY.md      # Para liderança
│   ├── FRAMEWORK_ANALYSIS.md     # Análise técnica
│   ├── MIGRATION_ROADMAP.md      # Plano 11 semanas
│   ├── PHASE3_IMPLEMENTATION_SUMMARY.md
│   ├── PI_AF_INTEGRATION.md
│   ├── PHASE3_ML_GUIDE.md
│   ├── QUICK_START_PHASE3.txt
│   └── PHASE2_GUIDE.md
├── .claude/
│   └── rules/
│       └── BOT_RULES.md          # Padrões de código
├── requirements.txt              # Dependências Python
├── pyproject.toml                # Config Python
├── run_app.py                    # Entry point
├── README.md                     # Raiz do projeto
└── safeplan.db                   # Database SQLite

```

---

## 📊 Status Atual

| Item | Status | Dados |
|------|--------|-------|
| Sensores no banco | ✅ Produção | 9.964 sensores ativos |
| Framework Streamlit | ⚠️ Prototipagem | Funcional mas inescalável |
| Crescimento previsto | 🔴 Crítico | 15.000+ sensores até 2027 |
| Solução recomendada | ✅ Aprovado | React + FastAPI |
| Timeline migração | 📅 Pendente | 11 semanas se iniciado agora |

---

## 🎯 Navegação por Perfil

### 👔 **Se você é Gestor/CIO:**
1. Leia **EXECUTIVE_SUMMARY.md** (5 min)
2. Aprove **MIGRATION_ROADMAP.md** timeline
3. Aloque recursos (8 pessoas)

### 🏗️ **Se você é Arquiteto/Tech Lead:**
1. Estude **FRAMEWORK_ANALYSIS.md** (15 min)
2. Detalhe **MIGRATION_ROADMAP.md** (20 min)
3. Aprove **BOT_RULES.md** padrões

### 💻 **Se você é Developer:**
1. Leia **BOT_RULES.md** (regras obrigatórias)
2. Execute **QUICK_START_PHASE3.txt** (setup local)
3. Siga padrões ao criar código novo

### 🔬 **Se você é Data Scientist/ML Engineer:**
1. Consulte **PHASE3_ML_GUIDE.md**
2. Veja estrutura em `src/ml/`
3. Valide dados em `tests/`

---

## 🔄 Fluxo de Trabalho de Documentação

### Atualizando documentação?

1. ✅ Não crie novos arquivos `.md` sem necessidade
2. ✅ Centralize em `docs/` (esta pasta)
3. ✅ Atualize este `README.md` com link
4. ✅ Siga **BOT_RULES.md** regra 2 (documentação centralizada)
5. ✅ Referencie no `docs/README.md`

---

## 📞 Contatos Importantes

| Função | Nome | Contato |
|--------|------|---------|
| Tech Lead | [Definir] | [Email] |
| DevOps | [Definir] | [Email] |
| Data Owner | [Definir] | [Email] |

---

## 📌 Checklist de Leitura (Recomendado)

- [ ] Li **EXECUTIVE_SUMMARY.md**
- [ ] Entendo por que Streamlit não escala
- [ ] Aprovei a arquitetura React + FastAPI
- [ ] Conheço o timeline de 11 semanas
- [ ] Li **BOT_RULES.md** (se developer)
- [ ] Entendo a estrutura de pastas em `.claude/rules/`

---

**Última atualização:** 22 de Fevereiro de 2026  
**Responsável:** SafePlan Architecture Team  
**Versão:** 1.0

Para dúvidas sobre documentação, consulte **BOT_RULES.md** Regra 2 (Documentação Centralizada).
