
# 🚀 SafePlan - Guias Rápidos

Bem-vindo ao SafePlan! Escolha um guia:

## 📖 Guias Disponíveis

### 🎯 **Para Começar** 
- **[SETUP_OPTIONS.md](SETUP_OPTIONS.md)** - 3 formas diferentes de fazer setup
  - Opção 1: Sem Terminal (setup.bat) ⭐ Mais Fácil
  - Opção 2: Com Terminal (Linha de Comando) 
  - Opção 3: Hub Gráfico (Interface Visual) ⭐ Mais Bonito

### 📚 **Documentação Completa**
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Guia detalhado em português
  - Pré-requisitos
  - Fluxo completo passo a passo
  - Referência de scripts
  - Troubleshooting

### 📦 **Distribuição & Empacotamento**
- **[DISTRIBUTION.md](DISTRIBUTION.md)** - Como empacotar para distribuição
  - Script Batch (Mais Simples)
  - PyInstaller (Executável)
  - NSIS (Instalador)

### 📊 **Projeto Principal**
- **[README.md](README.md)** - Documentação técnica completa

---

## ⚡ 30 Segundos - Comece Agora

### Se não gosta de terminal:
```
1. Clique duplo em: setup.bat
2. Responda as perguntas
3. Clique duplo em: dashboard.bat
4. Pronto!
```

### Se gosta de terminal:
```bash
python scripts/setup_credentials.py
python scripts/init_db.py
python scripts/discover_sensors_from_af.py --demo
python scripts/import_sensors_from_buzios.py
streamlit run app/main.py
```

### Se quer interface gráfica:
```bash
streamlit run app/control_hub.py
```

---

## 🎯 Escolha Seu Caminho

| Seu Perfil | Guia | Comando |
|-----------|------|---------|
| 👶 Iniciante total | [SETUP_OPTIONS.md](SETUP_OPTIONS.md) Opção 1 | Double-click setup.bat |
| 💻 Técnico | [GETTING_STARTED.md](GETTING_STARTED.md) Opção 2 | Terminal commands |
| 🎨 Visual | [SETUP_OPTIONS.md](SETUP_OPTIONS.md) Opção 3 | streamlit run app/control_hub.py |
| 📦 Para distribuir | [DISTRIBUTION.md](DISTRIBUTION.md) | pyinstaller ou batch |

---

## 📝 Estrutura de Documentos

```
SafePlan/
├── README.md                    <- Documentação técnica
├── GETTING_STARTED.md           <- Guia passo a passo
├── SETUP_OPTIONS.md             <- 3 formas de começar
├── DISTRIBUTION.md              <- Como empacotar
│
├── setup.bat                    <- Automático (Opção 1)
├── open_hub.bat                 <- Abre Control Hub
├── dashboard.bat                <- Abre Dashboard
│
└── app/
    ├── main.py                  <- Dashboard
    └── control_hub.py           <- Interface gráfica
```

---

## ✅ Checklist Rápido

- [ ] Python 3.10+ instalado
- [ ] Arquivo `docs/Sensores.xlsx` disponível
- [ ] Acesso ao PI Server (opcional, pode usar DEMO)
- [ ] Escolheu seu método de setup acima
- [ ] Pronto para começar! 🚀

---

## 🆘 Ajuda Rápida

**"Não sei por onde começar"**
→ Leia [SETUP_OPTIONS.md](SETUP_OPTIONS.md) e escolha uma opção

**"Recebi um erro"**
→ Veja seção de Troubleshooting em [GETTING_STARTED.md](GETTING_STARTED.md)

**"Quero distribuir para outros"**
→ Leia [DISTRIBUTION.md](DISTRIBUTION.md)

**"Quero entender o projeto todo"**
→ Leia [README.md](README.md)

---

**Começar agora:** [SETUP_OPTIONS.md](SETUP_OPTIONS.md) 👈
