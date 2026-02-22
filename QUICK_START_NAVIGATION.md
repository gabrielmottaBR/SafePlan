# ⚡ Quick Start: Navegação em Links

## O que foi adicionado?

✨ **Links navegáveis na tela de monitoramento** que abrem:

1. 📊 **Tela de Detalhes do Sensor** - Ao clicar no TAG
2. 🔗 **Tela de Detalhes do Grupo de Votação** - Ao clicar no Grupo

---

## 🎯 Uso Rápido

### 1. Abrir a aplicação
```bash
streamlit run app/main.py
```

### 2. Ir para monitoramento
```
http://localhost:8501/monitoring_page
```

### 3. Clicar em um TAG (ícone 🔍)
```
[:mag: AST-10001]  ← Clique aqui
```
**Abre:** Página com gráficos, histórico e detalhes do sensor

### 4. Clicar em um Grupo (ícone 🔗)
```
[:link: HULL_FT_5252801_CH4]  ← Clique aqui
```
**Abre:** Página com análise agregada de todos os sensores do grupo

### 5. Navegar entre páginas
- 📍 De sensor → clique "Ver Detalhes do Grupo" para grupo
- 📍 De grupo → clique "Detalhes" em um sensor para sensor individual
- 📍 De qualquer página → clique "← Voltar" para retornar

---

## 📁 Arquivos Criados/Modificados

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `app/pages/sensor_detail_page.py` | ✨ NOVO | Detalhes individual do sensor |
| `app/pages/voting_group_detail_page.py` | ✨ NOVO | Detalhes do grupo de votação |
| `app/pages/monitoring_page.py` | 🔧 MODIFICADO | Adicionados links em 4 visualizações |
| `src/data/repositories.py` | 🔧 MODIFICADO | 3 novos métodos + factory method |
| `NAVIGATION_GUIDE.md` | ✨ NOVO | Documentação completa |
| `IMPLEMENTATION_SUMMARY.md` | ✨ NOVO | Resumo de implementação |

---

## 🎨 Visualizações com Links

### Tabela Detalhada
```
┌─────┬──────────────┬──────┬────────┬──────────────────────┐
│ UEP │ TAG          │ Tipo │ Estado │ Grupos de Votação    │
├─────┼──────────────┼──────┼────────┼──────────────────────┤
│ P74 │ [:mag: 10001]│ CH4  │ Ok     │ [:link: HULL_FT...]  │
└─────┴──────────────┴──────┴────────┴──────────────────────┘
       ↑ Clicável                      ↑ Clicável
```

### Tabela Compacta
```
🏢 P74 (15 sensores)
   🔗 Grupo: [:link: HULL_FT_5252801_CH4] (3 sensores)
   ┌────────┬───────┬────────┐
   │ TAG    │ Tipo  │ Valor  │
   ├────────┼───────┼────────┤
   │ [:mag: │ CH4   │ 2.5 ppm│
   │  10001]│       │        │
   └────────┴───────┴────────┘
```

### Cards
```
┌──────────────────────────────────┐
│ 🟢 P74                           │
│ [:mag: AST-10001]                │
│                                  │
│ Tipo: CH4        Estado: Ok      │
│ Valor: 2.5 ppm | 0.5 mA          │
│ [:link: HULL_FT_5252801_CH4]     │
└──────────────────────────────────┘
```

---

## 📊 Página de Sensor

**Mostra:**
- Gráficos das últimas 24 horas e 7 dias
- Tipo de gás, unidade, plataforma
- Configuração de thresholds
- Grupo de votação + sensores do grupo
- Botão para ir ao grupo

**Exemplo de URL:**
```
http://localhost:8501/monitoring_page?sensor_id=AST-10001
```

---

## 🔗 Página de Grupo

**Mostra:**
- Gráficos agregados de todos os sensores
- Seletor de período: 24 horas / 7 dias / 30 dias
- Lista de sensores (abas por tipo de gás)
- Estatísticas (total, habilitados, tipos, plataformas)
- Botões "Detalhes" para cada sensor

**Exemplo de URL:**
```
http://localhost:8501/monitoring_page?voting_group=HULL_FT_5252801_CH4
```

---

## 🔍 Métodos de Repositório Adicionados

```python
# Buscar sensor pelo ID do PI AF
sensor = repo.get_by_id_af('AST-10001')

# Buscar todos os sensores de um grupo
sensores = repo.get_by_grupo('HULL_FT_5252801_CH4')

# Buscar leituras no período
leituras = repo.get_readings_for_sensor(
    sensor_id=1, 
    start=datetime.now() - timedelta(hours=24),
    end=datetime.now()
)

# Factory para criar repositórios dinamicamente
repo = RepositoryFactory.create_repository('sensor', db)
```

---

## 🧪 Teste Rápido

1. **Verificar síntaxe:**
   ```bash
   python -m py_compile app/pages/sensor_detail_page.py
   python -m py_compile app/pages/voting_group_detail_page.py
   python -m py_compile app/pages/monitoring_page.py
   python -m py_compile src/data/repositories.py
   ```

2. **Executar app:**
   ```bash
   streamlit run app/main.py
   ```

3. **Testar navegação:**
   - Abrir: `http://localhost:8501/monitoring_page`
   - Clicar em um TAG
   - Verificar se abre página de sensor
   - Clicar em um Grupo
   - Verificar se abre página de grupo
   - Clicar em "Voltar" ou links internos

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Link não funciona | Verifique URL em `http://localhost:8501` |
| Página em branco | Objeto sensor não encontrado no banco - importa dados com `discover_sensors_from_af.py` |
| Gráfico vazio | Sem leituras no período - gera dados com `generate_monitoring_data.py` |
| Erro ao clicar | Verifique console do Streamlit para detalhes |

---

## 📚 Documentação Completa

Para entender implementação em detalhes:
- `NAVIGATION_GUIDE.md` - Guia completo de uso
- `IMPLEMENTATION_SUMMARY.md` - Resumo técnico
- `docs/` - Documentação do projeto

---

## ✅ Checklist

- ✅ Links navegáveis na monitoramento
- ✅ Página de detalhes do sensor com gráficos
- ✅ Página de detalhes do grupo com análise agregada
- ✅ Navegação bidirecional entre páginas
- ✅ Query parameters para estado da URL
- ✅ Métodos de repositório para busca
- ✅ Sem dependências novas necessárias

---

**Pronto para usar!** 🚀

Abra `http://localhost:8501/monitoring_page` e comece a clicar nos links.
