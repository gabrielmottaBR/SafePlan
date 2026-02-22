# 🚀 Guia de Início Rápido - SafePlan

## 📋 Pré-requisitos

- Python 3.10+
- Acesso ao PI Server (SAURIOPIAF02)
- Acesso ao Excel com sensor paths (Sensores.xlsx)

## ⚡ Quick Start em 2 Minutos

É tudo o que você precisa:

```bash
# 1. Configurar credenciais (detecta username Windows automaticamente)
python scripts/setup_credentials.py

# 2. Setup completo (banco + sensores + dados)
python scripts/init_db.py
python scripts/discover_sensors_from_af.py
python scripts/import_sensors_from_buzios.py
python scripts/create_sample_data.py

# 3. Abrir dashboard
streamlit run app/main.py
```

Pronto! Acesse em: **http://localhost:8501**

---

## 🔐 Configuração de Credenciais

### Opção 1: Configuração Automática (Recomendado ✨)

Use o script de setup que detecta automaticamente seu username Windows e solicita a senha:

```bash
python scripts/setup_credentials.py
```

Este script irá:
- ✅ Detectar automaticamente seu username Windows
- ✅ Solicitar sua senha do PI Server de forma segura (não exibe na tela)
- ✅ Confirmar a senha
- ✅ Salvar no `.env` com permissões restritas
- ✅ Validar a configuração

### Opção 2: Configuração Manual

Se preferir configurar manualmente, siga os passos abaixo.

### 1. Configure o arquivo `.env`

Copie `.env.example` para `.env` (ou crie um novo):

```bash
cp .env.example .env
```

### 2. Edite o `.env` com suas credenciais

Abra `.env` e configure seus dados do PI Server:

```dotenv
# PI Server Configuration - Configure com suas credenciais!
PI_SERVER_HOST=pi-server.petrobras.local
PI_SERVER_USERNAME=seu_usuario
PI_SERVER_PASSWORD=sua_senha
```

⚠️ **IMPORTANTE:** 
- O arquivo `.env` está no `.gitignore` e **NUNCA será commitado**
- Não compartilhe o arquivo `.env` - cada usuário deve ter o seu próprio
- Senhas sensíveis devem estar apenas no `.env` local

## 🔄 Fluxo de Setup dos Sensores

### Passo 1: Configurar Credenciais

```bash
python scripts/setup_credentials.py
```

Detecta automaticamente seu username Windows e solicita a senha de forma segura.

### Passo 2: Inicializar o Banco de Dados

```bash
python scripts/init_db.py
```

Cria a estrutura do banco de dados (SensorConfig, Reading, Alert, etc).

### Passo 3: Descobrir Sensores do PI AF

```bash
python scripts/discover_sensors_from_af.py
```

Isso irá:
- Ler os paths de sensores do Excel (Sensores.xlsx)
- Conectar ao PI AF Server (usando credenciais do `.env`)
- Extrair 10 atributos de cada sensor: ID, TIPO_GAS, TIPO_LEITURA, GRUPO, etc
- Salvar em `config/sensor_paths_buzios.json` (9,983 sensores)

**Modo Demo (sem conexão ao PI):**
```bash
python scripts/discover_sensors_from_af.py --demo
```

### Passo 4: Importar Sensores para o Banco

```bash
python scripts/import_sensors_from_buzios.py
```

Isso irá:
- Ler o arquivo JSON gerado no passo anterior
- Criar registros no banco de dados
- Configurar thresholds padrão por tipo de gás
- Criar regras de alerta automáticas

### Passo 5: Gerar Dados de Teste (Opcional)

```bash
python scripts/create_sample_data.py
```

Popula leituras de exemplo para testar o dashboard.

### Passo 6: Iniciar o Dashboard

```bash
streamlit run app/main.py
```

Acesse em: **http://localhost:8501**

---

## 📊 Scripts Disponíveis

| Script | Descrição | Quando Usar |
|--------|-----------|------------|
| `setup_credentials.py` | Configura credenciais automaticamente | Primeiro setup (recomendado) |
| `init_db.py` | Inicializa banco de dados | Primeiro setup |
| `discover_sensors_from_af.py` | Descobre sensores do PI AF | Primeiro setup ou atualiza lista |
| `import_sensors_from_buzios.py` | Importa sensores para banco | Após descoberta |
| `create_sample_data.py` | Gera dados de teste | Testes e demonstração |
| `test_af_connectivity.py` | Testa conexão com PI AF | Diagnóstico de conectividade |
| `test_phase2.py` | Testes de integração | Validação de sistema |

---

## 🐛 Troubleshooting

### "PI_SERVER_PASSWORD not configured"

Certifique-se de que o arquivo `.env` existe e tem as credenciais preenchidas:
```bash
cat .env
```

### "Could not connect to PI Server"

Execute para diagnosticar:
```bash
python scripts/test_af_connectivity.py
```

### "Arquivo Sensores.xlsx não encontrado"

O arquivo deve estar em `docs/Sensores.xlsx`. Verifique se foi extraído do PI Builder.

---

## 📁 Estrutura do Projeto

```
SafePlan/
├── .env                          # Configurações (não versionado)
├── .env.example                  # Template de configuração
├── app/                          # Aplicação Streamlit
│   ├── main.py                   # Dashboard principal
│   └── pages/                    # Páginas do dashboard
├── config/
│   ├── settings.py               # Carregamento de config
│   └── sensor_paths_buzios.json  # Sensores descobertos
├── scripts/
│   ├── discover_sensors_from_af.py    # Descober sensores
│   ├── import_sensors_from_buzios.py  # Importar para DB
│   ├── init_db.py                     # Inicializar DB
│   └── ...                            # Outros utilitários
├── src/
│   ├── data/                     # Models & Repositories
│   ├── pi_server/                # Integração PI AF
│   ├── ml/                       # ML & Anomaly Detection
│   ├── alerting/                 # Alertas & Teams
│   └── sensors/                  # Gerenciador de Sensores
└── requirements.txt              # Dependências Python
```

---

## 💡 Dicas Úteis

### Para Re-importar Sensores

Se precisar limpar e importar novamente:

```bash
# 1. Limpar BD anterior (cria novo)
python scripts/init_db.py

# 2. Descobrir novamente
python scripts/discover_sensors_from_af.py

# 3. Importar
python scripts/import_sensors_from_buzios.py
```

### Para Usar Dados de Teste

```bash
# Pular descoberta real e usar dados de exemplo
python scripts/discover_sensors_from_af.py --demo
python scripts/import_sensors_from_buzios.py
python scripts/create_sample_data.py
streamlit run app/main.py
```

### Aumentar Verbosidade

```bash
python scripts/discover_sensors_from_af.py --verbose
```

---

## 🔗 Referência de Atributos PI AF

Os seguintes atributos são extraídos de cada sensor:

| Atributo | Campo | Usar Para |
|----------|-------|-----------|
| ID | id_af | Identificação única do sensor |
| TIPO_GAS | tipo_gas | Classificação (CH4, H2S, CO2, O2, etc) |
| TIPO_LEITURA | tipo_leitura | Unidade (ppm, %, obscuration %, etc) |
| GRUPO | grupo | Grupo de votação para bypass/override |
| Descricao | descricao | Descrição do sensor |
| FABRICANTE | fabricante | Fabricante/Modelo |
| Tipo | tipo | Tipo da sensor baseado em gas |
| UEP | uep | Plataforma (P74, P75, FPAB, FPAT, etc) |

---

## ❓ Dúvidas?

Consulte o README.md principal para documentação detalhada do projeto.
