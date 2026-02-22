# SafePlan - Integração com PI AF Server SAURIOPIAF02

## 📋 Visão Geral

O SafePlan agora pode buscar dados diretamente do servidor PI AF (Asset Framework) da Petrobras, especificamente do **SAURIOPIAF02\DB_BUZIOS_SENSORES**.

Isso permite:
- ✅ Ler dados de sensores de fogo/gás em tempo real
- ✅ Monitorar múltiplas plataformas (P74-P79, FPAB, FPAT)
- ✅ Explorar automaticamente a hierarquia de sensores
- ✅ Importar sensores com configuração automática de thresholds

---

## 🔌 Pré-requisitos

1. **PI AF SDK instalado** no local padrão:
   ```
   C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0
   ```

2. **Conexão com SAURIOPIAF02** acessível desde sua máquina

3. **Python 3.8+** com IronPython/pythonnet para suportar .NET assemblies

4. **Credentials** com acesso à database DB_BUZIOS_SENSORES

---

## 🚀 Como Usar

### Passo 1: Descobrir Sensores Disponíveis

```bash
python scripts/discover_sensor_paths.py
```

Este script:
1. Conecta ao SAURIOPIAF02
2. Explora a estrutura da database DB_BUZIOS_SENSORES
3. Identifica sensores de fogo/gás
4. Gera arquivo `config/sensor_paths_buzios.json` com mapeamento

**Saída esperada:**
```
[1/5] Conectando ao AF Server SAURIOPIAF02...
✓ Conectado com sucesso

[2/5] Obtendo database DB_BUZIOS_SENSORES...
✓ Database obtido com sucesso

[3/5] Explorando estrutura da database...
DATABASE: DB_BUZIOS_SENSORES
ROOT ELEMENTS: 9
==================================================

Plataformas encontradas:
  • P74: 12 elementos
  • P75: 10 elementos
  • P76: 8 elementos
  ...

Resumo de sensores por tipo:
  • CH4_POINT: 28 sensores
  • H2S: 15 sensores
  • TEMPERATURE: 10 sensores
  ...

[4/5] Buscando sensores de fogo/gás...
✓ Encontrados 98 sensores

[5/5] Criando arquivo de mapeamento...
✓ Arquivo criado: config/sensor_paths_buzios.json

Total de sensores encontrados: 98
```

### Passo 2: Importar Sensores para SafePlan

```bash
# Inicializar banco se necessário
python scripts/init_db.py

# Importar sensores
python scripts/import_sensors_from_af.py
```

Este script:
1. Lê mapeamento de sensores
2. Configura thresholds automáticos baseados no tipo
3. Cria alert rules padrão
4. Persiste tudo no banco SQLite

**Saída esperada:**
```
[1/4] Inicializando banco de dados...
✓ Banco inicializado

[2/4] Carregando mapeamento de sensores...
✓ 98 sensores para importar

[3/4] Conectando ao AF Server...
✓ Conectado

[4/4] Importando sensores...
────────────────────────────────────────
✓ [1/98] P74_CH4_POINT_1
✓ [2/98] P74_CH4_POINT_2
✓ [3/98] P74_H2S_1
...

════════════════════════════════════════
RESUMO DA IMPORTAÇÃO
════════════════════════════════════════
Total processado: 98
✓ Importados com sucesso: 98
⚠ Pulados/Erros: 0
════════════════════════════════════════

✓ Sensores importados com sucesso!
```

### Passo 3: Verificar no Dashboard

```bash
streamlit run app/main.py
```

Acesse em http://localhost:8501 e vá para **Configuration** para ver os sensores importados.

---

## 📂 Arquivos da Integração

```
SafePlan/
├── config/
│   ├── config_gideaopi.json           # Configuração do AF Server
│   └── sensor_paths_buzios.json       # Mapeamento gerado (após descoberta)
│
├── src/pi_server/
│   ├── gideao_pi.py                  # Biblioteca adaptada do Petrobras
│   ├── af_manager.py                 # Gerenciador de AF Database
│   ├── pi_client.py                  # Wrapper atualizado
│   └── data_fetcher.py               # Fetcher para AF & PI
│
└── scripts/
    ├── discover_sensor_paths.py       # Descobrir sensores
    └── import_sensors_from_af.py      # Importar sensores
```

---

## 📊 Estrutura de Dados do AF

A database **DB_BUZIOS_SENSORES** organiza sensores desta forma:

```
\\SAURIOPIAF02\DB_BUZIOS_SENSORES
├── Buzios (Root Element)
│   ├── P74
│   │   ├── HULL
│   │   │   ├── HULL_H011
│   │   │   │   ├── CH4_Point
│   │   │   │   ├── H2S_Detector
│   │   │   │   └── Temperature_Sensor
│   │   │   └── HULL_H012
│   │   └── TOPSIDES
│   ├── P75
│   │   ├── HULL
│   │   └── TOPSIDES
│   ├── P76, P77, P78, P79
│   ├── FPAB
│   └── FPAT
```

Cada sensor é um **elemento AF com atributos** que contêm:
- Valor corrente (snapshot)
- Histórico de valores
- Unidade de medida
- Metadados

---

## ⚙️ Thresholds Padrão

Os sensors são importados com thresholds automáticos baseados no tipo:

### CH4 (Metano)
```
Lower OK: 0 ppm
Lower Warning: 5 ppm
Upper Warning: 50 ppm
Upper Critical: 100 ppm
```

### H2S (Sulfeto de Hidrogênio)
```
Lower OK: 0 ppm
Lower Warning: 1 ppm
Upper Warning: 10 ppm
Upper Critical: 20 ppm
```

### CO2 (Dióxido de Carbono)
```
Lower OK: 0 ppm
Lower Warning: 100 ppm
Upper Warning: 5000 ppm
Upper Critical: 10000 ppm
```

### FLAME (Deteccão de Chama)
```
Lower OK: 0
Lower Warning: 1
Upper Warning: 2
Upper Critical: 3
```

### TEMPERATURE (Temperatura)
```
Lower OK: -10°C
Lower Warning: 20°C
Upper Warning: 60°C
Upper Critical: 80°C
```

*Vous pouvez ajustar estes valores na interface web após importação*

---

## 🔍 Explorando a Estrutura Manualmente

Se quiser explorar a database AF manualmente:

```python
import sys
from src.pi_server import gideao_pi
from src.pi_server.af_manager import AFDatabaseManager

# Conecta
af_server = gideao_pi.getServidor('SAURIOPIAF02', 'AF')
db = gideao_pi.getAFDataBase('DB_BUZIOS_SENSORES', af_server)

# Explora
manager = AFDatabaseManager(db)
manager.print_structure()

# Busca sensores específicos
ch4_sensors = manager.get_sensor_paths()
p74_sensors = manager.get_sensor_paths(platform='P74')

# Obtém valor corrente
sensor_path = r"\\SAURIOPIAF02\DB_BUZIOS_SENSORES\Buzios\P74\HULL\CH4_Sensor|Value"
current_value = gideaoPI.getValorCorrente(db, sensor_path)
print(f"Current value: {current_value}")

# Obtém valores históricos
import pandas as pd
df = gideaoPI.getValoresInterpolados(db, sensor_path, '*-24h', '*', '1h')
print(df)
```

---

## 🐛 Troubleshooting

### Erro: "OSIsoft.AF not found"

**Problema:** PI AF SDK não está no local esperado

**Solução:** Verif no arquivo `config/config_gideaopi.json`:
```json
{
  "path_pi": "C:\\Program Files (x86)\\PIPC\\AF\\PublicAssemblies\\4.0",
  "af_sdk": "OSIsoft.AFSDK"
}
```

Se o caminho estiver diferente, atualize o arquivo.

### Erro: "Connection timeout"

**Problema:** Não conseguiu conectar ao SAURIOPIAF02

**Solução:**
1. Verifique se SAURIOPIAF02 está acessível: `ping seuriopiaf02`
2. Verifique credenciais de rede (Windows do usuário)
3. Execute em máquina com acesso ao network corporativo

### Erro: "Database not found"

**Problema:** DB_BUZIOS_SENSORES não existe no servidor

**Solução:** Verifique o nome exato e permissões - pode ser:
- Sensível a maiúsculas/minúsculas
- Requer credenciais especiais

---

## 📈 Próximas Fases

As seguintes features estão planejadas:

- [ ]  Agendador automático para refresh de dados (a cada 20-30s)
- [ ] Cache de dados históricos com sincronização com AF
- [ ] Edição de thresholds via UI com persistência
- [ ] Histórico de mudanças de configuração
- [ ] Validação de atributos do AF (type checking, units)

---

## 📚 Referências

- **Arquivo de configuração:** `config/config_gideaopi.json`
- **Biblioteca wrapper:** `src/pi_server/gideao_pi.py`
- **AF Database manager:** `src/pi_server/af_manager.py`
- **Documento original (referência):** `/Python/pyee-master/01_python_basico_PI/gideao_pi.py`

---

## ✅ Verificação Rápida

Para verificar se tudo está funcionando:

```bash
# 1. Descobrir sensores
python scripts/discover_sensor_paths.py

# 2. Verificar arquivo gerado
cat config/sensor_paths_buzios.json | head -50

# 3. Importar (se satisfeito com descoberta)
python scripts/import_sensors_from_af.py

# 4. Verificar no banco
python scripts/test_phase2.py

# 5. Ver no dashboard
streamlit run app/main.py
# Vá para Configuration tab
```

---

**Status:** Integração com PI AF Server ✅ Pronta para uso
**Próximo:** Fase 3 de ML Integration
