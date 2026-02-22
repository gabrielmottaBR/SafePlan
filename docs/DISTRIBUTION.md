# 📦 Empacotamento do SafePlan - Guia Completo

Este documento descreve as opções para empacotar o SafePlan para distribuição sem depender de Python/terminal.

---

## 🎯 Opções de Distribuição

### **Opção 1: Script Batch (Mais Simples) ✨ RECOMENDADO**

**Para quem:** Usuários com Windows, não familiarizados com terminal

**Como usar:**
1. Execute `setup.bat` - Faz todo o setup com cliques Next
2. Execute `open_hub.bat` - Abre interface gráfica de controle
3. Execute `dashboard.bat` - Abre o dashboard

**Vantagens:**
- ✅ Nenhuma dependência extra
- ✅ Simples de entender para usuário final
- ✅ Fácil de debugar
- ✅ Python já deve estar instalado (pré-requisito)

**Desvantagens:**
- Requer Python instalado
- Terminal fica visível

---

### **Opção 2: Control Hub Streamlit (Interface Gráfica)**

**Para quem:** Usuários que querem interface visual

**Como usar:**
```bash
# Primeira vez
python setup.bat

# Depois, abra o Control Hub:
.\open_hub.bat
```

**Vantagens:**
- ✅ Interface gráfica intuitiva
- ✅ Sem terminal
- ✅ Botões atraentes
- ✅ Status visual do projeto

**Desvantagens:**
- Requer Streamlit (já incluído em requirements.txt)
- Usa porta 8501

---

### **Opção 3: PyInstaller (Executável Standalone)**

**Para quem:** Distribuição profissional, sem Python instalado

**Instalação:**
```bash
pip install pyinstaller
```

**Criar executáveis dos scripts:**
```bash
# Criar hub executável
pyinstaller --onefile --console app/control_hub.py -n SafePlanHub

# Criar setup executável  
pyinstaller --onefile --console scripts/setup_credentials.py -n SafePlanSetup
```

**Resultado:**
- `dist/SafePlanHub.exe` - Control Hub em exe
- `dist/SafePlanSetup.exe` - Setup em exe

**Vantagens:**
- ✅ Executável standalone
- ✅ Não requer Python instalado
- ✅ Profissional

**Desvantagens:**
- ⚠️ Arquivo grande (~100-200 MB)
- ⚠️ Requer mais espaço em disco
- ⚠️ Tempo de rebuild maior

---

### **Opção 4: Instalador NSIS (Profissional)**

**Para quem:** Distribuição empresarial com instalador Windows

**O que faz:**
- Instalador `.exe` como qualquer software Windows
- Menu Iniciar com atalhos
- Desinstalador
- Verificação de Python

**Instalação:**
1. Instale NSIS de http://nsis.sourceforge.net/
2. Use o arquivo `installer.nsi` (veja exemplo abaixo)

**Vantagens:**
- ✅ Instalador profissional
- ✅ Menu Iniciar
- ✅ Desinstalador
- ✅ Familiar para usuários Windows

**Desvantagens:**
- Mais complexo de criar
- Requer NSIS instalado

---

## 🚀 Recomendação por Cenário

### Distribuição Interna (Mesma empresa/rede)
→ **Use Opção 1 ou 2** (setup.bat + open_hub.bat)
- Simples
- Python já deve estar disponível
- Fácil de manter

### Distribuição Externa (Fora da empresa)
→ **Use Opção 3** (PyInstaller)
- Executável standalone
- Sem depender de Python instalado
- Mais profissional

### Distribuição Empresarial (Larga escala)
→ **Use Opção 4** (NSIS)
- Instalador como qualquer software
- Menu Iniciar
- Suporte a atualização

---

## 📋 Passos para Criar com PyInstaller

### 1. Instalar PyInstaller
```bash
pip install pyinstaller
```

### 2. Criar Executável do Control Hub
```bash
pyinstaller --onefile ^
  --windowed ^
  --name SafePlanHub ^
  --icon icon.ico ^
  app/control_hub.py
```

Resultado: `dist/SafePlanHub.exe`

### 3. Criar Executável do Setup
```bash
pyinstaller --onefile ^
  --console ^
  --name SafePlanSetup ^
  scripts/setup_credentials.py
```

Resultado: `dist/SafePlanSetup.exe`

### 4. Copiar Necessidades
O PyInstaller cria uma pasta `dist/` com o .exe. Você precisa também copiar:
- Pasta `app/` (páginas do Streamlit)
- Pasta `config/` (configurações)
- Pasta `src/` (código)
- Arquivo `requirements.txt`
- Arquivo `.env.example`

### 5. Empacotar Tudo
```bash
# Criar pasta de distribuição
mkdir SafePlan_Distribution
xcopy dist\SafePlanHub.exe SafePlan_Distribution\
xcopy app SafePlan_Distribution\app\ /E
xcopy config SafePlan_Distribution\config\ /E
xcopy src SafePlan_Distribution\src\ /E
copy requirements.txt SafePlan_Distribution\
copy .env.example SafePlan_Distribution\

# Compactar
tar -czf SafePlan_v1.0.zip SafePlan_Distribution/
```

---

## 💡 Dica: Script Batch para Distribuição

Para facilitar a distribuição, crie um `distribuir.bat`:

```batch
@echo off
REM Script para criar distribuição do SafePlan

echo Buildando executáveis com PyInstaller...
pip install pyinstaller

echo.
echo [1/3] Criando SafePlanHub.exe...
pyinstaller --onefile --windowed --name SafePlanHub app/control_hub.py

echo [2/3] Criando SafePlanSetup.exe...
pyinstaller --onefile --console --name SafePlanSetup scripts/setup_credentials.py

echo [3/3] Preparando distribuição...
mkdir dist\SafePlan_v1.0
xcopy dist\SafePlanHub.exe dist\SafePlan_v1.0\ /Y
xcopy app dist\SafePlan_v1.0\app\ /E /Y
xcopy config dist\SafePlan_v1.0\config\ /E /Y
xcopy src dist\SafePlan_v1.0\src\ /E /Y
copy requirements.txt dist\SafePlan_v1.0\
copy .env.example dist\SafePlan_v1.0\

echo.
echo [SUCESSO] Distribuição pronta em: dist\SafePlan_v1.0
echo Compacte a pasta para: SafePlan_v1.0.zip
```

---

## 🎁 Exemplo: NSIS Installer Script

Salve como `installer.nsi`:

```nsis
; SafePlan Installer
Name "SafePlan v1.0"
OutFile "SafePlan-Setup-v1.0.exe"
InstallDir "$PROGRAMFILES\SafePlan"

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\SafePlan_v1.0\*.*"
  
  ; Criar atalho no Menu Iniciar
  CreateDirectory "$SMPROGRAMS\SafePlan"
  CreateShortCut "$SMPROGRAMS\SafePlan\Control Hub.lnk" "$INSTDIR\SafePlanHub.exe"
  CreateShortCut "$SMPROGRAMS\SafePlan\Desinstalar.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\SafePlan"
SectionEnd
```

**Compilar:**
```bash
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
```

Resultado: `SafePlan-Setup-v1.0.exe`

---

## ✅ Checklist de Distribuição

- [ ] Testar em máquina limpa (sem Python)
- [ ] Testar em Windows 10/11
- [ ] Testar em Windows 7/8 (se compatibilidade for necessária)
- [ ] Incluir `.env.example` com instruções
- [ ] Incluir `README.md` em arquivo de distribuição
- [ ] Incluir `GETTING_STARTED.md`
- [ ] Testar todos os cenários:
  - [ ] Setup credenciais
  - [ ] Descobrir sensores (modo DEMO)
  - [ ] Importar sensores
  - [ ] Abrir dashboard
- [ ] Criar versão com versionamento (v1.0, v1.1, etc)

---

## 📝 Próximas Etapas

### Curto Prazo (Distribuição Atual)
1. Use `setup.bat` para setup manual
2. Use `open_hub.bat` para abrir Control Hub
3. Distribua como ZIP

### Médio Prazo
1. Criar executáveis com PyInstaller
2. Testar em máqunas sem Python

### Longo Prazo
1. Criar instalador NSIS
2. Setup de auto-update
3. Suporte técnico automatizado

---

## 🆘 Troubleshooting de Distribuição

**Problema: Arquivo .exe muito grande**
→ Use `--onefile` com `--strip` para PyInstaller

**Problema: Antivírus bloqueia .exe**
→ Normal para executáveis Python compactados
→ Solução: Assinar executável com certificado

**Problema: Não encontra módulos**
→ Use `--hidden-import=nome_modulo` no PyInstaller

---

## 📚 Referências

- [PyInstaller Documentation](https://pyinstaller.org/)
- [NSIS Documentation](http://nsis.sourceforge.net/Docs/)
- [Streamlit Deployment](https://docs.streamlit.io/library/deploy)
