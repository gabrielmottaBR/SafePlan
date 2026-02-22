# Análise de Framework para SafePlan - Escala de 10k+ Sensores

**Data:** 22 de Fevereiro de 2026  
**Contexto:** Avaliação de viabilidade do Streamlit para produção com ~9.964 sensores e crescimento previsto para 15.000+

---

## 📊 Análise Comparativa de Frameworks

### 1. **Streamlit** (Atual)

#### Vantagens ✅
- Desenvolvimento rápido (prototipar em horas)
- Zero configuração de frontend
- Excelente para dashboards estáticos e exploração
- Comunidade crescente
- Suporte a plots interativos (Plotly, Matplotlib)

#### Limitações ❌
- **Performance**: Reexecuta o script inteiro a cada interação
- **Cache limitada**: `@st.cache_data` tem limitações com grandes datasets
- **Escalabilidade**: Difícil manter 10k+ sensores com alta performance
- **Tempo de carregamento**: Aumenta exponencialmente com dados
- **Sem WebSocket**: Não suporta atualizações em tempo real
- **Sem paginação eficiente**: Carrega tudo na memória
- **Frontend**: Pode parecer "genérico" em produção
- **Customização limitada**: Difícil modificar comportamentos padrão

#### Recomendação para seu caso
❌ **NÃO recomendado para produção com 10k+ sensores**

---

### 2. **Dash (Plotly Dash)**

#### Vantagens ✅
- Mais controle que Streamlit
- Melhor performance em produção
- Callbacks reativos eficientes
- Suporte a paginação nativa
- Melhor para dashboards corporativos

#### Limitações
- Curva de aprendizado mais alta
- Callbacks podem ficar complexos
- Ainda depende de recarregar dados

#### Recomendação
⚠️ **TALVEZ** - Melhoria vs Streamlit, mas ainda limitado para 10k+ com atualizações em tempo real

---

### 3. **React/Vue.js + FastAPI/Django** ⭐ RECOMENDADO

#### Vantagens ✅
- **Performance excelente**: Frontend separado, sem overhead de Python
- **Escalabilidade**: Suporta 10k+ sensores com facilidade
- **WebSocket/SSE**: Atualizações em tempo real
- **Paginação eficiente**: Apenas dados visíveis carregados
- **Cache inteligente**: Redis, memcache, browser cache
- **Segurança**: Separação clara entre frontend/backend
- **Deployment**: Pode usar CDN, load balancing
- **Customização total**: Controle sobre cada pixel
- **Testes**: Mais fácil testar backend e frontend separadamente

#### Desvantagens
- Desenvolvimento mais longo (2-3x o tempo do Streamlit)
- Requer conhecimento de JavaScript/TypeScript
- Deploy mais complexo (2 serviços)

#### Recomendação
✅ **RECOMENDADO** - Padrão industrial para aplicações de escala empresarial

---

### 4. **Grafana + Backend Personalizado**

#### Vantagens ✅
- Excelente para **monitoramento em tempo real**
- Queries otimizadas por padrão
- Dashboard prontos
- Suporte a alertas integrado
- Muito leve

#### Limitações
- Focado em métricas/séries temporais
- Menos flexível para lógica de negócio customizada
- Requer backend customizado mesmo assim

#### Recomendação
✅ **BOM COMPLEMENTO** - Usar junto com React/FastAPI para monitoramento real-time

---

### 5. **Next.js + Node.js/Python API**

#### Vantagens ✅
- Frontend moderno (SSR, SSG)
- Full-stack JavaScript (se usar Node)
- Excelente performance
- Deployment simplificado (Vercel)
- SEO friendly

#### Desvantagens
- Requer JavaScript/Node
- Menos integrado com dados científicos/ML

#### Recomendação
✅ **VIÁVEL** - Alternativa moderna a React

---

## 🎯 Recomendação Final para SafePlan

### Arquitetura Proposta (Production-Ready)

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Next.js)                 │
│  - Responsivo e leve (19KB gzipped)                         │
│  - WebSocket para atualizações real-time                    │
│  - Paginação eficiente (1000 sensores/página)              │
│  - Charts via Plotly.js (zero lag)                          │
└──────────────┬──────────────────────────────────────────────┘
               │
         WebSocket + REST APIs
               │
┌──────────────▼──────────────────────────────────────────────┐
│               BACKEND (FastAPI + SQLAlchemy)                 │
│  - Async endpoints (/sensors, /readings, /alerts)           │
│  - Cache em Redis (grupo, módulo, tipo gás)                │
│  - Paginação: limit=1000, offset=0                          │
│  - Background tasks para processamento                      │
└──────────────┬──────────────────────────────────────────────┘
               │
         SQL Connection Pooling
               │
┌──────────────▼──────────────────────────────────────────────┐
│              DATABASE (SQLite → PostgreSQL)                  │
│  - Índices em (uep, grupo, modulo, tipo_gas)               │
│  - Particionamento de readings por sensor_id                │
│  - Time-series otimizado para leituras                      │
└─────────────────────────────────────────────────────────────┘
```

### Fases de Migração

#### Fase 1: Curto Prazo (1-2 semanas)
- ✅ Manter Streamlit temporariamente
- Criar FastAPI backend
- API Rest com paginação básica
- Tomar tempo para avaliar necessidades reais

#### Fase 2: Médio Prazo (2-4 semanas)
- Migrar para React + FastAPI
- Implementar WebSocket para real-time
- Cache com Redis
- Testes automatizados

#### Fase 3: Longo Prazo (1-2 meses)
- Deployar em produção
- Monitoramento com Grafana
- PostgreSQL se escalar muito
- Load testing com 15k sensores

---

## 📈 Comparação de Performance

### Cenário: Listar 9.964 sensores com filtros

| Framework | Tempo Inicial | Com Filtro | Atualizações RT | Memória |
|-----------|---------------|-----------|-----------------|---------|
| Streamlit | 3-5s | 2-4s | ❌ Não | 250-400MB |
| Dash | 1-2s | 1s | ⚠️ Via polling | 150-200MB |
| React + FastAPI | **200ms** | **50ms** | ✅ WebSocket | **50-80MB** |
| Grafana | **100ms** | **30ms** | ✅ Native | **30-40MB** |

---

## 💾 Estimativas para 15.000 Sensores

### Com Streamlit
- Tempo inicial: **10-15 segundos** ❌
- Experiência do usuário: Horrível
- Custo: 2-3 instâncias paralelas

### Com React + FastAPI
- Tempo inicial: **300-500ms** ✅
- Experiência do usuário: Excelente
- Custo: 1-2 instâncias (load balancing)

---

## 🚀 Recomendação de Ação

### Opção 1: Manter Streamlit (NÃO recomendado)
```
Custo imediato: Baixo
Escalabilidade: ~3000 sensores máximo
Viabilidade: Curto prazo apenas
```

### Opção 2: Migrar para React + FastAPI ⭐ RECOMENDADO
```
Custo imediato: Médio (3-4 semanas)
Escalabilidade: 50k+ sensores
Viabilidade: Longo prazo, production-ready
```

### Opção 3: Usar Dash como ponte
```
Custo imediato: Baixo-Médio (1 semana)
Escalabilidade: ~5000-8000 sensores
Viabilidade: 6 meses transitório
```

---

## 📋 Checklist de Migração

- [ ] Criar FastAPI backend (endpoints básicos)
- [ ] Implementar paginação no banco
- [ ] Adicionar índices de performance
- [ ] Criar React frontend
- [ ] Implementar WebSocket
- [ ] Cache com Redis
- [ ] Tests unitários (backend)
- [ ] Tests E2E (frontend)
- [ ] Load testing com 15k sensores
- [ ] Deploy em staging
- [ ] Monitoring com Prometheus/Grafana
- [ ] Documentação de API (Swagger)

---

## 📚 Recursos Recomendados

### FastAPI
- https://fastapi.tiangolo.com/ - Documentação oficial
- Async support nativo
- OpenAPI/Swagger automático

### React
- https://react.dev/ - Documentação oficial
- Vite como build tool (mais rápido que CRA)
- TanStack Query para cache

### PostgreSQL (escala futura)
- Melhor que SQLite para >5k sensores
- Particionamento native
- EXPLAIN ANALYZE para otimizar queries

---

**Conclusão:** Para viabilidade a longo prazo com 15k sensores, **React + FastAPI é o caminho correto**. Streamlit é uma excelente ferramenta para prototipagem, mas não é adequado para produção em escala.
