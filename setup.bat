@echo off
REM SafePlan - Setup Automático para Windows
REM Execute este arquivo para configurar o projeto

setlocal enabledelayedexpansion
cd /d "%~dp0"

cls
echo.
echo ============================================================================
echo   SafePlan - Configurador Automático
echo ============================================================================
echo.
echo Este script vai:
echo   1. Instalar dependências Python
echo   2. Configurar credenciais do PI Server
echo   3. Inicializar banco de dados
echo   4. Descobrir sensores do PI AF
echo   5. Importar sensores para o banco
echo.
pause

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERRO] Python não encontrado!
    echo.
    echo Instale Python 3.10+ de: https://www.python.org/downloads/
    echo Certifique-se de marcar "Add Python to PATH" durante a instalação.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Instalar requirements
echo Instalando dependências...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependências
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Passo 1: Configurar Credenciais
echo ============================================================================
echo.
python scripts/setup_credentials.py
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao configurar credenciais
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Passo 2: Inicializar Banco de Dados
echo ============================================================================
echo.
python scripts/init_db.py
if errorlevel 1 (
    echo [ERRO] Falha ao inicializar banco
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Passo 3: Descobrir Sensores do PI AF
echo ============================================================================
echo.
echo Escolha uma opção:
echo   1. Conectar ao PI AF Server REAL (requer acesso à rede)
echo   2. Usar modo DEMO (dados de exemplo, sem conexão)
echo.
set /p choice="Escolha (1 ou 2) [padrão: 2]: "
if "!choice!"=="" set choice=2

if "!choice!"=="1" (
    echo.
    echo Conectando ao PI AF Server...
    python scripts/discover_sensors_from_af.py
) else (
    echo.
    echo Usando modo DEMO...
    python scripts/discover_sensors_from_af.py --demo
)

if errorlevel 1 (
    echo [ERRO] Falha ao descobrir sensores
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Passo 4: Importar Sensores para o Banco
echo ============================================================================
echo.
python scripts/import_sensors_from_buzios.py
if errorlevel 1 (
    echo [ERRO] Falha ao importar sensores
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Passo 5: Gerar Dados de Teste (Opcional)
echo ============================================================================
echo.
set /p test="Deseja gerar dados de teste? (S/N) [padrão: S]: "
if "!test!"=="" set test=S

if /i "!test!"=="S" (
    python scripts/create_sample_data.py
    if errorlevel 1 (
        echo [aviso] Falha ao gerar dados de teste (não crítico)
    )
)

echo.
echo ============================================================================
echo [SUCESSO] Configuração completa!
echo ============================================================================
echo.
echo Próximo passo: Iniciar o Dashboard
echo.
set /p launch="Deseja abrir o dashboard agora? (S/N) [padrão: S]: "
if "!launch!"=="" set launch=S

if /i "!launch!"=="S" (
    echo.
    echo Iniciando Streamlit...
    echo Seu navegador abrirá em: http://localhost:8501
    echo.
    streamlit run app/main.py
) else (
    echo.
    echo Para iniciar o dashboard depois, execute:
    echo   streamlit run app/main.py
    echo.
    pause
)

endlocal
