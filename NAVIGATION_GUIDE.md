# 🔗 Navegação e Links nas Telas de Detalhamento

## Visão Geral

A tela de monitoramento (`http://localhost:8501/monitoring_page`) agora possui links navegáveis que permitem:

1. **Clicar no TAG de um sensor** para abrir a tela de detalhamento individual
2. **Clicar no Grupo de Votação** para abrir a tela de detalhamento do grupo
3. **Navegar entre as telas** de forma intuitiva

---

## 📊 Tela de Monitoramento (`monitoring_page.py`)

### Links Disponíveis

#### 1. Links nos TAGs (Sensores)
- **Formato:** `:mag: TAG_ID` (ícone de lupa + TAG)
- **Ação:** Clique abre a página de detalhes do sensor
- **Disponível em:** 
  - Tabela Detalhada
  - Tabela Compacta
  - Detalhes PI AF
  - Cards

**Exemplo:**
```
[:mag: AST-10001](/?sensor_id=AST-10001)
```

#### 2. Links nos Grupos de Votação
- **Formato:** `:link: GRUPO_NAME` (ícone de link + Nome do grupo)
- **Ação:** Clique abre a página de detalhes do grupo
- **Disponível em:**
  - Tabela Detalhada
  - Tabela Compacta
  - Detalhes PI AF
  - Cards

**Exemplo:**
```
[:link: HULL_FT_5252801_CH4](/?voting_group=HULL_FT_5252801_CH4)
```

---

## 🔍 Tela de Detalhamento do Sensor (`sensor_detail_page.py`)

### Conteúdo Exibido

**Header com informações do sensor:**
- `ID do sensor no PI AF` (título principal)
- Descrição do sensor

**Informações Básicas (3 colunas):**
- 🏢 **Plataforma (UEP):** P74, P75, FPAB, FPAT, etc.
- ⚗️ **Tipo de Gás:** CH4, H2S, CO2, O2, FLAME, etc.
- 📐 **Unidade de Medida:** ppm, %, level, obscuration%, etc.

**Gráficos Históricos:**
- Sensibilização (últimas 24 horas)
- Sensibilização (últimos 7 dias)
- Com interatividade do Plotly (zoom, pan, hover)

**Dados do Sensor:**
- ID do PI AF Server
- Descrição/Tag no PI
- Caminho completo no PI AF
- Fabricante

**Configuração de Thresholds:**
- OK Inferior / Superior
- Aviso Inferior / Superior
- Crítico
- Status (Habilitado/Desabilitado)

**Grupos de Votação:**
- Nome do grupo
- Todos os sensores no grupo em tabela
- Link para detalhes do grupo

**Auditoria:**
- Data de criação
- Data de última atualização

### Navegação

- **Botão "Voltar":** Remove query parameter e volta para monitoramento
- **Botão "Ver Detalhes do Grupo de Votação":** Navega para a página de grupo

---

## 🔗 Tela de Detalhamento do Grupo de Votação (`voting_group_detail_page.py`)

### Conteúdo Exibido

**Header:**
- Nome do grupo de votação
- Total de sensores no grupo

**Estatísticas (4 colunas):**
- Total de Sensores
- Sensores Habilitados
- Tipos de Gás únicos
- Plataformas únicas

**Gráfico Histórico Agregado:**
- Uma série por sensor do grupo
- Período selecionável: 24 horas / 7 dias / 30 dias
- Visualização comparativa de todos os sensores

**Lista de Sensores do Grupo:**
- Organizados por abas (uma aba por tipo de gás)
- Cada sensor com:
  - ID do sensor (ícone 📌)
  - UEP / Tipo / Status / Descrição
  - Unidade de medida
  - Botão "Detalhes" para abrir página do sensor individual

**Resumo dos Sensores:**
- Tabela com todos os campos:
  - TAG, UEP, Tipo, Unidade, Status, Descrição

### Navegação

- **Botão "Voltar":** Remove query parameter e volta para monitoramento
- **Botão "Detalhes" (em cada sensor):** Navega para a página de detalhes daquele sensor específico

---

## 🔄 Fluxo de Navegação

```
┌─────────────────────────────────────────────────────────────┐
│         MONITORAMENTO (monitoring_page.py)                   │
│                                                               │
│  Tabela com sensores e grupos de votação                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ UEP  │ TAG            │ Tipo │ Grupos Votação      │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │ P74  │ [:mag: AST-...]│ CH4  │ [:link: HULL_FT...] │    │
│  └──────────────────────────────────────────────────────┘    │
│         ↓ Click TAG             ↓ Click Grupo                │
│         ↓                       ↓                             │
└─────────────────────────────────────────────────────────────┘
         │                         │
         ↓                         ↓
  ┌──────────────────┐    ┌────────────────────┐
  │  SENSOR DETAIL   │    │ VOTING GROUP DETAIL│
  │  (sensor_detail  │    │ (voting_group_     │
  │   _page.py)      │    │  detail_page.py)   │
  │                  │    │                    │
  │ - ID AF Server   │    │ - Sensores Grupo   │
  │ - Tipo Gás       │    │ - Histórico Agr.   │
  │ - Gráficos       │    │ - Estatísticas     │
  │ - Thresholds     │    │ - Links para each  │
  │ - Grupo Info     │←───┤   sensor           │
  │ - Voltar         │    │ - Voltar           │
  │ - Ver Grupo      └────→                    │
  └──────────────────┘    └────────────────────┘
         ↑                         ↑
         └─────────────────────────┘
         Navegação bidirecional
         entre Sensor ↔ Grupo
```

---

## 🛠️ Implementação Técnica

### Query Parameters

A navegação usa `st.query_params` do Streamlit:

```python
# Para sensor:
st.query_params['sensor_id'] = 'AST-10001'

# Para grupo:
st.query_params['voting_group'] = 'HULL_FT_5252801_CH4'
```

### Métodos de Repositório Adicionados

**SensorConfigRepository:**
- `get_by_id_af(id_af: str)` - Busca sensor pelo ID do PI AF
- `get_by_grupo(grupo: str)` - Busca sensores de um grupo

**SensorReadingRepository:**
- `get_readings_for_sensor(sensor_id, start, end)` - Busca leituras no período

**RepositoryFactory:**
- `create_repository(repo_type, db)` - Factory para criar repositórios dinamicamente

### Arquivos Modificados

1. **app/pages/monitoring_page.py**
   - Adicionados links markdown para TAGs e Grupos
   - Links em 4 formatos de visualização diferentes

2. **app/pages/sensor_detail_page.py** (NOVO)
   - Página de detalhes individual do sensor
   - Gráficos históricos
   - Informações completas do sensor
   - Navegação para grupo de votação

3. **app/pages/voting_group_detail_page.py** (NOVO)
   - Página de detalhes do grupo de votação
   - Somatória de sensores do grupo
   - Gráficos agregados
   - Navegação para sensores individuais

4. **src/data/repositories.py**
   - Novos métodos: `get_by_id_af`, `get_by_grupo`, `get_readings_for_sensor`
   - Factory method: `create_repository`

---

## 📱 Experiência do Usuário

### Cenário 1: Investigar um Sensor Específico

1. Na monitoramento, o usuário vê tabela com sensores
2. Clica no link `:mag: AST-10001`
3. Abre página com detalhes completos do sensor
4. Vê gráficos históricos e configuração
5. Vê quais outros sensores estão no mesmo grupo de votação
6. Clica em "Ver Detalhes do Grupo de Votação" para análise comparativa

### Cenário 2: Analisar Comportamento do Grupo

1. Na monitoramento, o usuário vê grupos em coluna separada
2. Clica no link `:link: HULL_FT_5252801_CH4`
3. Abre página com gráficos agregados de todos os sensores do grupo
4. Vê análise comparativa e estatísticas
5. Se nota anomalia, clica em "Detalhes" de um sensor específico
6. Volta ao grupo ou retorna à monitoramento

### Cenário 3: Rastrear Histórico

1. Usuário abre detalhes de sensor
2. Visualiza gráfico das últimas 24 horas
3. Se identifica padrão, clica no gráfico para zoom
4. Navega para a página do grupo para comparação
5. Ajusta período de tempo (24h / 7d / 30d) no seletor

---

## ⚙️ Configuração

Nenhuma configuração adicional necessária. As páginas:

- Usam o banco de dados já existente
- Acessam dados via repositories da camada de dados
- Funcionam com ou sem sensores no banco
- Mostram mensagens informativas se dados não disponíveis

---

## 🐛 Resolução de Problemas

### "Nenhum sensor selecionado"

**Causa:** Você abriu a página diretamente sem clicar em um link
**Solução:** Volte à página de monitoramento e clique em um TAG

### "Sensor não encontrado no banco"

**Causa:** O ID_AF não existe na base de dados
**Possível solução:**
- Execute discovery de sensores: `python scripts/discover_sensors_from_af.py`
- Execute importação: `python scripts/import_sensors_from_buzios.py`

### Gráficos vazios

**Causa:** Sem leituras no período selecionado
**Solução:**
- Generate dados de teste: `python scripts/generate_monitoring_data.py`
- Aguarde coleta real de dados do PI AF

### Links não funcionam

**Verificação:**
1. Confirme que está em `http://localhost:8501`
2. Atualize página (F5) se necessário
3. Verifique console do Streamlit (deve rodar sem erros)

---

## 📈 Melhorias Futuras

Possíveis enhancements:

1. **Alertas na página de detalhes**
   - Mostrar alertas ativos do sensor
   - Histórico de alertas disparados

2. **Export de dados**
   - Exportar gráficos como PNG/PDF
   - Exportar dados históricos como CSV

3. **Configuração de Thresholds**
   - Editar limites diretamente na página
   - Salvar para histórico de audit

4. **Comparação entre sensores**
   - Selecionar múltiplos sensores para comparação
   - Gráfico sobreposto lado a lado

5. **Dashboard customizável**
   - Favoritos de sensores
   - Abas personalizadas por grupo

---

**Versão:** 1.0  
**Data:** Fevereiro 2026  
**Autor:** SafePlan Development Team
