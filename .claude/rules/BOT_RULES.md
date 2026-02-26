# Regras e Instruções de Comportamento do Agente Copilot

**Documentação de Governança de Código - SafePlan Project**

Estas instruções garantem consistência estrutural e qualidade do código. O agente Copilot deve seguir rigorosamente as diretrizes abaixo ao gerar, revisar ou modificar código.

---

## 📁 Regra 1: Organização de Pastas e Estrutura

Mantenha a estrutura de pastas organizada e divida por funcionalidades:

- **Backend**: `src/` (data, sensors, ml, alerting, pi_server, scheduler, utils)
- **Frontend**: `app/` (main.py, pages/)
- **Testes**: `tests/` (unit/, integration/)
- **Documentação**: `docs/`
- **Scripts**: `scripts/`
- **Configuração**: `config/`

**Regras específicas:**
- ❌ Nunca crie arquivos soltos na raiz do projeto
- ✅ Mantenha testes organizados em `tests/` com estrutura espelhando `src/`
- ✅ Separe backend (src/) e frontend (app/) de forma estrita
- ✅ Evite misturar código de diferentes camadas (data/business/presentation)

**Exemplos corretos:**
```
src/data/models.py      ✅
src/data/repositories.py ✅
tests/unit/test_data_layer.py ✅
docs/FRAMEWORK_ANALYSIS.md ✅
```

**Exemplos incorretos:**
```
Models.py          ❌
test_models.py     ❌ (deve ser em tests/unit/)
FRAMEWORK_ANALYSIS.md ❌ (deve ser em docs/)
```

---

## 📚 Regra 2: Documentação Centralizada

A documentação deve ser centralizada e evita redundância:

- ✅ **Centralizar** em `docs/` com um arquivo README principal
- ✅ **Referenciar** documentação no README raiz
- ✅ Use um arquivo por categoria: `docs/FRAMEWORK_ANALYSIS.md`, `docs/ARCHITECTURE.md`
- ❌ **Nunca** crie `.md` para cada funcionalidade pequena
- ❌ **Nunca** deixe documentação fora da pasta `docs/`
- ❌ **Nunca** crie múltiplos arquivos `README.md` em diferentes pastas
- ❌ **Nunca** crie `.md` sem a solicitação do usário


**Estrutura recomendada:**
```
docs/
  ├── QUICK_START.md
  ├── ARCHITECTURE.md
  ├── FRAMEWORK_ANALYSIS.md
  ├── API_REFERENCE.md
  └── DEPLOYMENT.md
```

---

## 🔤 Regra 3: Convenções de Nomenclatura

Siga rigorosamente as convenções Python:

| Elemento | Convenção | Exemplos |
|----------|-----------|----------|
| Arquivos | `snake_case` | `sensor_manager.py` ✅ / `SensorManager.py` ❌ |
| Funções | `snake_case` | `fetch_sensor_data()` / `get_readings_by_id()` |
| Classes | `PascalCase` | `SensorManager`, `SensorConfig`, `AlertEngine` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_SENSORS = 15000`, `DEFAULT_TIMEOUT = 30` |
| Variáveis | `snake_case` | `sensor_id`, `alert_level`, `platform_name` |
| Privado | `_leading_underscore` | `_internal_helper()`, `_cache_data` |

**Avoid:**
- ❌ Abreviações confusas: `snsr`, `cfg`, `mgr`
- ❌ Nomes genéricos: `data`, `result`, `value`
- ❌ Misturar convenções no mesmo arquivo

---

## 🎯 Regra 4: Qualidade e Legibilidade de Código

Mantenha código limpo e compreensível:

### Complexidade
- ✅ Prefira soluções simples e diretas
- ✅ Máximo 20 linhas por função (regra prática)
- ✅ Use type hints obrigatoriamente
- ❌ Evite código "clever" que seja difícil de entender

### Comentários
- ✅ Explique o **porquê**, não o **o quê**
- ✅ Use para lógica não-óbvia
- ❌ Não comente óbvios: `i = 0  # Set i to 0`

### Exemplo correto:
```python
def fetch_sensor_readings(sensor_id: str, hours: int = 24) -> List[Reading]:
    """Fetch sensor readings from the last N hours."""
    # Filter by timestamp to optimize query
    start_time = datetime.now() - timedelta(hours=hours)
    return db.query(Reading).filter(Reading.created_at >= start_time).all()
```

---

## 🔧 Regra 5: Modularidade e Responsabilidade Única

Divida funcionalidades em unidades bem-definidas:

- ✅ Cada classe com uma responsabilidade
- ✅ Funções com máximo 15-20 linhas
- ✅ Acoplamento mínimo entre módulos
- ✅ Use dependency injection ao invés de imports circulares
- ❌ Classes/funções "god objects" com múltiplas responsabilidades

**Exemplo anti-padrão:**
```python
class DataProcessor:  # ❌ Faz tudo
    def fetch_data(self): ...
    def process(self): ...
    def save(self): ...
    def send_email(self): ...
    def generate_report(self): ...
```

**Exemplo correto:**
```python
class SensorDataRepository:  # ✅ Uma responsabilidade
    def fetch(self, sensor_id: str) -> List[Reading]: ...
    def save(self, reading: Reading) -> None: ...
```

---

## 🔐 Regra 6: Segurança e Dados Sensíveis

Proteja credenciais e dados sensíveis:

- ✅ **Sempre use variáveis de ambiente** para credenciais
- ✅ **Nunca commitar** `.env` ou chaves privadas
- ✅ Use `python-dotenv` ou sistema de secrets
- ✅ Valide e sanitize inputs
- ✅ Registre acesso a dados sensíveis
- ❌ Hardcoded credentials em código
- ❌ Log de senhas ou tokens

**Exemplo correto:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
PI_SERVER_PASSWORD = os.getenv('PI_SERVER_PASSWORD')
if not PI_SERVER_PASSWORD:
    raise ValueError("PI_SERVER_PASSWORD not configured")
```

---

## ✅ Regra 7: Código Executável e Sem Erros

Garantir que todo código está pronto para produção:

- ✅ **Sempre** testar antes de submeter
- ✅ **Zero** erros de sintaxe
- ✅ **Sem** imports não usados
- ✅ **Sem** TODO incompleto (exceto com contexto claro)
- ✅ Usar placeholders apenas com comentários explicativos
- ❌ Deixar código em progresso
- ❌ Funcionalidades "half-baked"

**Exemplo:**
```python
# ❌ NÃO FAÇA ISTO
def new_feature():
    # TODO: implementar isso
    pass

# ✅ FAÇA ASSIM
def validate_sensor_input(sensor_id: str) -> bool:
    """Validate sensor ID format."""
    # Placeholder: Future implementation for complex validation
    return bool(sensor_id) and len(sensor_id) > 0
```

---

## 💬 Regra 8: Uso Racional do Agente

Estruture requisições de forma eficiente:

- ✅ Divida tarefas em etapas menores (máx. 3-5 partes por requisição)
- ✅ Peça revisão de cada parte antes da próxima
- ✅ Valide sintaxe após cada alteração
- ✅ Use iterações pequenas para maior qualidade
- ❌ Solicitar 500 linhas de código de uma vez
- ❌ Requisições vagas sem contexto
- ❌ Tentar fazer tudo em uma chamada

**Exemplo bom de requisição:**
```
1. Crie a função `validate_sensor_data()`
2. Após validar, implemente o método `save_to_db()`
3. Finalmente, adicione testes unitários
```

---

## 📋 Checklist de Implementação

Antes de submeter código:

- [ ] Estrutura em pastas corretas (Regra 1)
- [ ] Sem documentação redundante (Regra 2)
- [ ] Nomenclatura consistente (Regra 3)
- [ ] Código legível e simples (Regra 4)
- [ ] Responsabilidades bem-separadas (Regra 5)
- [ ] Sem credenciais em código (Regra 6)
- [ ] Testado e sem erros (Regra 7)
- [ ] Divisão lógica de tarefas (Regra 8)

---

## 📞 Referência Rápida

| Dúvida | Resposta |
|--------|----------|
| Onde colocar novo arquivo? | Na pasta apropriada em `src/` ou `app/`, nunca na raiz |
| Posso criar README em subfolder? | Não - documentação centralizada em `docs/` |
| Qual nome para nova classe? | `PascalCase` - ex: `SensorValidator` |
| Posso usar `i`, `x`, `tmp`? | Apenas em loops triviais; use nomes descritivos |
| Como documentar função? | Docstring + type hints, comentários só se não-óbvio |
| Onde colocar credenciais? | Variáveis de ambiente (`.env`), NUNCA em código |
| Função muito longa? | Refatore em múltiplas menores com responsabilidades claras |

---

**Última Atualização:** 22 de Fevereiro de 2026  
**Versão:** 1.1  
**Responsável:** SafePlan Architecture Team
