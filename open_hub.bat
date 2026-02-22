@echo off
REM Abre o SafePlan Control Hub
REM Execute este arquivo para abrir o painel de controle

setlocal
cd /d "%~dp0"

echo.
echo Abrindo SafePlan Control Hub...
echo.

streamlit run app/control_hub.py

endlocal
