# Roadmap de Migração Arquitetural - SafePlan

**Versão:** 1.0  
**Data:** 22 de Fevereiro de 2026  
**Status:** Proposta para Aprovação

---

## 🎯 Objetivo

Migrar SafePlan de **Streamlit** (solução prototipagem) para **React + FastAPI** (solução production-ready) para suportar crescimento de 10k para 15k+ sensores com performance, escalabilidade e robustez.

---

## 📊 Contexto Atual

| Métrica | Valor | Status |
|---------|-------|--------|
| Sensores no banco | 9,964 | ✅ Operacional |
| Crescimento previsto | 15,000+ | ⚠️ Não escalável com Streamlit |
| Framework atual | Streamlit | ❌ Inviável em produção |
| Tempo página inicial | 3-5s | ❌ Inaceitável |
| Suporte real-time | ❌ | ❌ Importante para alertas |
| Load balancing | ❌ | ❌ Necessário para escala |

---

## 🏗️ Arquitetura Proposta

```
┌──────────────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)                     │
│  • SPA responsivo (19KB gzipped)                              │
│  • TanStack Query para cache inteligente                      │
│  • Plotly.js para gráficos interativos                        │
│  • WebSocket para alertas real-time                           │
│  • Deploy: Vercel/Netlify ou S3+CloudFront                    │
└──────────────────┬───────────────────────────────────────────┘
                   │ REST API + WebSocket
                   │ (CORS habilitado)
┌──────────────────▼───────────────────────────────────────────┐
│                   BACKEND (FastAPI)                            │
│  • uvicorn com gunicorn multiprocess                          │
│  • Async endpoints (/sensors, /readings, /alerts)            │
│  • Cache Redis (grupo, módulo, agregações)                   │
│  • Rate limiting e autenticação JWT                           │
│  • OpenAPI/Swagger automático                                 │
│  • Deploy: Docker containers + Kubernetes/EC2                │
└──────────────────┬───────────────────────────────────────────┘
                   │ SQLAlchemy ORM + Connection pooling
                   │
┌──────────────────▼───────────────────────────────────────────┐
│                DATABASE (PostgreSQL)                           │
│  • Índices em (uep, grupo, modulo)                            │
│  • Particionamento de readings por sensor_id                  │
│  • Time-series otimizado                                      │
│  • Backups automáticos                                        │
│  • Replicação para HA                                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 📅 Plano de Implementação

### **Fase 1: Preparação (Semanas 1-2)**

#### Tarefa 1.1: Definir especificações técnicas
- [ ] Escolher hosting (AWS/Azure/GCP)
- [ ] Definir infra (Docker, Kubernetes vs simples)
- [ ] Planejar banco de dados (PostgreSQL vs SQLite)
- [ ] Preparar CI/CD pipeline

**Saída esperada:** Documento de arquitetura aprovado

#### Tarefa 1.2: Preparar ambiente de desenvolvimento
- [ ] Setup Node.js + npm/yarn
- [ ] Setup Python venv para FastAPI
- [ ] Configurar GitHub Actions/GitLab CI
- [ ] Template docker-compose para local dev

**Saída esperada:** Dev environment totalmente funcional

#### Tarefa 1.3: Migrar dados para PostgreSQL
- [ ] Backup do SQLite atual
- [ ] Migração schema SQLAlchemy
- [ ] Validação de integridade
- [ ] Teste de performance

**Saída esperada:** PostgreSQL com 9,964 sensores, sem dados perdidos

**Duração estimada:** 5-7 dias  
**Recursos:** 1 DBA + 1 Backend Developer

---

### **Fase 2: Backend FastAPI (Semanas 3-5)**

#### Tarefa 2.1: Setup projeto FastAPI
- [ ] Criar estrutura de projeto
- [ ] Configurar alembic para migrações
- [ ] Setup logging estruturado
- [ ] Autenticação JWT

**Endpoints base:**
```
GET    /api/sensors              # Lista com paginação
GET    /api/sensors/{id}         # Detalhe
GET    /api/sensors/grupo/{grupo} # Por grupo
GET    /api/readings/{sensor_id} # Histórico
POST   /api/alerts               # Criar alerta
WS     /ws/alerts               # WebSocket para altertas real-time
```

**Saída esperada:** API com 80% dos endpoints em funcionamento

#### Tarefa 2.2: Implementar paginação e caching
- [ ] Paginação eficiente (limit/offset)
- [ ] Setup Redis cache
- [ ] Cache strategy (TTL por endpoint)
- [ ] Invalidação de cache

**Saída esperada:** Resposta de 9.964 sensores em <100ms

#### Tarefa 2.3: Otimização de performance
- [ ] Índices de banco de dados
- [ ] EXPLAIN ANALYZE queries
- [ ] Connection pooling
- [ ] Gzip em respostas

**Saída esperada:** Load test com 1000 req/s simultâneas

**Duração estimada:** 10-14 dias  
**Recursos:** 1 Backend Lead + 1 Backend Developer

---

### **Fase 3: Frontend React (Semanas 6-8)**

#### Tarefa 3.1: Setup projeto React + Vite
- [ ] Criar app com `npm create vite@latest`
- [ ] Setup Tailwind CSS para styling
- [ ] Configurar ESLint + Prettier
- [ ] Setup Vitest para testes

**Saída esperada:** Boilerplate funcional

#### Tarefa 3.2: Implementar páginas principais
- [ ] Página de monitoramento (lista 9.964 sensores)
- [ ] Detalhe de sensor individual
- [ ] Filtros por grupo, módulo, tipo gás
- [ ] Gráficos com Plotly.js

**Saída esperada:** 3 páginas principais funcionando

#### Tarefa 3.3: Integração com backend
- [ ] Setup TanStack Query para cache
- [ ] Fetch de dados via API
- [ ] WebSocket para alertas real-time
- [ ] Tratamento de erros e loading states

**Saída esperada:** Frontend comunicando com FastAPI

**Duração estimada:** 10-14 dias  
**Recursos:** 1 Frontend Lead + 1 Frontend Developer

---

### **Fase 4: Integração e Testes (Semanas 9-10)**

#### Tarefa 4.1: Testes end-to-end
- [ ] Cypress/Playwright E2E tests
- [ ] Testes de performance (Lighthouse)
- [ ] Testes de segurança (OWASP)
- [ ] Teste de carga (Apache JMeter, k6)

**Meta:** >90 pontos Lighthouse, <500ms TTFB

#### Tarefa 4.2: Deployment em staging
- [ ] Docker images (frontend + backend)
- [ ] Kubernetes manifests ou Docker Compose
- [ ] GitHub Actions deploy automático
- [ ] Monitoramento com Prometheus/Grafana

**Saída esperada:** Pipeline CI/CD funcional

#### Tarefa 4.3: Documentação e treinamento
- [ ] API docs (Swagger)
- [ ] Guia de deployment
- [ ] Runbooks para troubleshooting
- [ ] Treinamento da equipe

**Saída esperada:** Documentação completa e equipe preparada

**Duração estimada:** 7-10 dias  
**Recursos:** QA Lead + DevOps + Tech Writer

---

### **Fase 5: Produção (Semana 11)**

#### Tarefa 5.1: Cutover
- [ ] Migração final de dados
- [ ] DNS cutover para novo sistema
- [ ] Validação em produção
- [ ] Monitoramento 24/7 durante 1 semana

#### Tarefa 5.2: Rollback plan
- [ ] Se problemas, reverter para Streamlit
- [ ] Backup de banco de dados
- [ ] Health checks automatizados

**Duração estimada:** 2-3 dias  
**Recursos:** Toda a equipe de operações

---

## 📊 Timeline Total

```
Semana  1-2   │ Preparação
Semana  3-5   │ Backend FastAPI
Semana  6-8   │ Frontend React
Semana  9-10  │ Integração e testes
Semana  11    │ Produção
─────────────────────────────
Total: ~11 semanas (2.5 meses)
```

---

## 💰 Recursos Necessários

### Humanos
- 1 Tech Lead/Arquiteto
- 2 Backend Developers (Python/FastAPI)
- 2 Frontend Developers (React/TypeScript)
- 1 QA Engineer
- 1 DevOps Engineer
- 1 DBA (migração dados)
- **Total: 8 pessoas**

### Infraestrutura
- PostgreSQL managed (AWS RDS)
- Redis managed (AWS ElastiCache)
- Kubernetes cluster (EKS)
- Load balancer (ALB/NLB)
- **Custo mensal estimado: $1,500-3,000**

---

## 🔄 Alternativa: Abordagem Incremental

Se não conseguir 8 pessoas simultâneas:

### Fase 1: FastAPI Backend Only (2-3 semanas)
- Criar API em FastAPI com dados existentes
- Manter Streamlit como frontend temporariamente
- Benefício: APIs já prontas para futuro React

### Fase 2: Migrar Página por Página
- Criar página em React (1-2 dias)
- Integrar com FastAPI
- Remover correspondente em Streamlit
- Risco: Menor

**Timeline:** 8-10 semanas (mais seguro)

---

## ⚠️ Riscos e Mitigação

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Perda de dados na migração | Crítico | 3x backup, validação completa |
| Downtime durante cutover | Crítico | Blue-green deployment |
| Performance insuficiente | Alto | Load tests semanais |
| Equipe não familiarizada | Médio | Treinamento antecipado |
| Scope creep | Médio | Foco em MVP apenas |

---

## ✅ Critérios de Sucesso

- [ ] **Performance:** Tempo página < 500ms para 9.964 sensores
- [ ] **Escalabilidade:** Suporta 15.000+ sensores sem degradação
- [ ] **Uptime:** 99.9% SLA em produção
- [ ] **Real-time:** Alertas chegam em <1 segundo
- [ ] **Segurança:** Passa auditoria OWASP Top 10
- [ ] **Desenvolvimento:** Time consegue deploy em <5 minutos

---

## 📝 Próximos Passos

1. **Aprovação** desta proposta pela liderança
2. **Alocação** dos 8 recursos necessários
3. **Kick-off** meeting para alinhar visão
4. **Fase 1** iniciada na próxima semana

---

## 📚 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Kubernetes Deployment](https://kubernetes.io/docs/tasks/run-application/run-stateless-application-deployment/)
- [System Design Interview](https://www.youtube.com/c/GauravSen) - Canal útil para design de sistemas em escala

---

**Nota:** Este documento é uma proposta baseada na análise technical. Ajustes podem ser necessários após alinhamento com stakeholders e definição de prioridades de negócio.
