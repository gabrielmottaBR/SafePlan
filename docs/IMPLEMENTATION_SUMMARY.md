# 🎯 Resumo das Telas de Detalhamento

## Arquivos Criados

### 1. **sensor_detail_page.py**
   - **Localização:** `app/pages/sensor_detail_page.py`
   - **Acesso:** Clique em um TAG na tela de monitoramento
   - **Query Param:** `?sensor_id=AST-10001`

### 2. **voting_group_detail_page.py**
   - **Localização:** `app/pages/voting_group_detail_page.py`
   - **Acesso:** Clique em um Grupo de Votação na tela de monitoramento
   - **Query Param:** `?voting_group=HULL_FT_5252801_CH4`

### 3. **NAVIGATION_GUIDE.md**
   - **Localização:** `NAVIGATION_GUIDE.md` (raiz do projeto)
   - **Documentação completa de uso e implementação**

---

## 🔄 Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────┐
│         CAMADA DE APRESENTAÇÃO (Streamlit)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  monitoring_page.py ──→ Links em 4 formatos:                    │
│  ├─ Tabela Detalhada                                            │
│  ├─ Tabela Compacta                                             │
│  ├─ Detalhes PI AF                                              │
│  └─ Cards                                                        │
│         │                                                         │
│         ├──→ sensor_detail_page.py (via ?sensor_id=...)         │
│         │     ├─ Detalhes do sensor                             │
│         │     ├─ Gráficos históricos (24h, 7d)                 │
│         │     ├─ Configuração de thresholds                     │
│         │     └─ Link para voting_group_detail_page.py          │
│         │                                                         │
│         └──→ voting_group_detail_page.py (via ?voting_group=...) │
│               ├─ Gráficos agregados do grupo                    │
│               ├─ Estatísticas do grupo                          │
│               ├─ Lista de sensores (abas por tipo gás)          │
│               └─ Links para sensor_detail_page.py               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         CAMADA DE DADOS (Repositories)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SensorConfigRepository                                          │
│  ├─ get_by_id_af(id_af) → SensorConfig                         │
│  └─ get_by_grupo(grupo) → List[SensorConfig]                    │
│                                                                   │
│  SensorReadingRepository                                         │
│  └─ get_readings_for_sensor(sensor_id, start, end)             │
│      → List[SensorReading]                                      │
│                                                                   │
│  RepositoryFactory                                              │
│  └─ create_repository(repo_type, db)                            │
│      → Repositório específico                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         CAMADA DE BANCO DE DADOS (SQLAlchemy)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SensorConfig                                                    │
│  ├─ sensor_id (PK)                                              │
│  ├─ id_af (🔍 searchable)                                       │
│  ├─ grupo (groupable)                                           │
│  ├─ tipo_gas, tipo_leitura, uep                                 │
│  └─ ...outros atributos PI AF                                  │
│                                                                   │
│  SensorReading                                                   │
│  ├─ reading_id (PK)                                             │
│  ├─ sensor_id (FK → SensorConfig)                               │
│  ├─ value, timestamp, unit                                      │
│  └─ Index: (sensor_id, timestamp)                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Modificações em Arquivos Existentes

### 1. **app/pages/monitoring_page.py**

**Antes:** Exibia dados em DataFrames simples
```python
st.dataframe(display_df, use_container_width=True)
```

**Depois:** Links navegáveis com:
- Ícones (`:mag:` para sensor, `:link:` para grupo)
- URLs com query parameters
- Suporte a markdown em colunas
- Links em todas as 4 visualizações

**Links adicionados:**
```python
# TAG (sensor)
tag_link = f"[:mag: {row['tag_detector']}](/?sensor_id={row['tag_detector']})"

# Grupo de votação
grupo_link = f"[:link: {row['grupos_votacao']}](/?voting_group={row['grupos_votacao']})"
```

### 2. **src/data/repositories.py**

**Novos métodos SensorConfigRepository:**
```python
def get_by_id_af(self, id_af: str) -> Optional[SensorConfig]:
def get_by_grupo(self, grupo: str) -> List[SensorConfig]:
```

**Novo método SensorReadingRepository:**
```python
def get_readings_for_sensor(self, sensor_id: int, start: datetime, 
                            end: datetime) -> List[SensorReading]:
```

**Novo método RepositoryFactory:**
```python
@staticmethod
def create_repository(repo_type: str, db):
    # Factory method para criação dinâmica de repositórios
```

---

## 🎨 Styling e UX

### Cores utilizadas
- **Header:** Gradiente roxo (#667eea → #764ba2)
- **Grupo:** Gradiente rosa (#f093fb → #f5576c)
- **Cards:** Bordas em tom primário

### Componentes interativos
- ✅ Botões com navegação
- ✅ Gráficos Plotly com zoom/pan
- ✅ Expandable sections
- ✅ Tabs para agrupamento
- ✅ Badges de status

### Responsividade
- 📱 Layout em colunas (1, 2, 3 colunas conforme contexto)
- 🖥️ Tabelas com scroll horizontal
- 📊 Gráficos que se adaptam à largura

---

## ✅ Checklist de Funcionalidades

### Sensor Detail Page
- ✅ Busca sensor pelo ID_AF
- ✅ Header com informações básicas
- ✅ Informações em 3 colunas (UEP, Tipo Gás, Unidade)
- ✅ Gráficos históricos (24h e 7d)
- ✅ Dados do sensor (PI AF, descrição, fabricante)
- ✅ Thresholds configuráveis
- ✅ Grupo de votação com lista de sensores
- ✅ Navegação para grupo de votação
- ✅ Botão voltar
- ✅ Informações de auditoria (datas)

### Voting Group Detail Page
- ✅ Busca grupo por nome
- ✅ Header com informações do grupo
- ✅ Estatísticas (total, habilitados, tipos, plataformas)
- ✅ Gráficos agregados com seletor de período
- ✅ Uma aba por tipo de gás
- ✅ Cada sensor com link para detalhes
- ✅ Tabela resumida de todos os sensores
- ✅ Navegação para sensores individuais
- ✅ Botão voltar

### Monitoring Page
- ✅ Links em "Tabela Detalhada"
- ✅ Links em "Tabela Compacta"
- ✅ Links em "Detalhes PI AF"
- ✅ Links em "Cards"
- ✅ Query params com sensor_id
- ✅ Query params com voting_group

### Repositories
- ✅ `get_by_id_af()` para sensores
- ✅ `get_by_grupo()` para grupos
- ✅ `get_readings_for_sensor()` para históricos
- ✅ Factory method para criação dinâmica

---

## 🚀 Como Testar

### 1. Iniciar a aplicação
```bash
streamlit run app/main.py
```

### 2. Navegar para monitoramento
```
http://localhost:8501/monitoring_page
```

### 3. Clicar em um sensor (link com 🔍)
- Exemplo: `[:mag: AST-10001]`
- Abre: `http://localhost:8501/monitoring_page?sensor_id=AST-10001`

### 4. Clicar em um grupo (link com 🔗)
- Exemplo: `[:link: HULL_FT_5252801_CH4]`
- Abre: `http://localhost:8501/monitoring_page?voting_group=HULL_FT_5252801_CH4`

### 5. Navegar entre páginas
- De sensor → para grupo (botão na página)
- De grupo → para sensor (clique em "Detalhes")
- De qualquer lugar → volta com botão "Voltar"

---

## 📦 Dependências

Nenhum pacote novo necessário. Utiliza:
- ✅ `streamlit` (já instalado)
- ✅ `pandas` (já instalado)
- ✅ `plotly` (já instalado)
- ✅ `sqlalchemy` (já instalado)

---

## 🔐 Questões de Segurança

- ✅ Query params sanitizados (SQL injection prevention)
- ✅ Usuário só vê sensores que existem no banco
- ✅ Nenhuma exposição de dados sensível nos params
- ✅ Mensagens de erro não revelam estrutura do banco

---

## 📈 Performance

- ✅ Queries otimizadas com índices existentes
- ✅ Caching de repositórios via Streamlit
- ✅ Gráficos lazy-loaded (gerados sob demanda)
- ✅ Paginação para grupos grandes (futuro)

---

## 🎓 Exemplos de URLs

```
# Sensor específico
http://localhost:8501/monitoring_page?sensor_id=AST-10001
http://localhost:8501/monitoring_page?sensor_id=CH4-Main%20Deck

# Grupo de votação
http://localhost:8501/monitoring_page?voting_group=HULL_FT_5252801_CH4
http://localhost:8501/monitoring_page?voting_group=SEPARATOR_FT_5252900_CO2

# Múltiplos parâmetros (navegação entre telas)
http://localhost:8501/monitoring_page?sensor_id=AST-10001&voting_group=...
```

---

**Status:** ✅ Implementação Completa  
**Data de Conclusão:** Fevereiro 2026  
**Versão:** 1.0
