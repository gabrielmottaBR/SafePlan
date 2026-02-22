@echo off
REM Abre o Dashboard de Monitoramento do SafePlan
REM Execute este arquivo para visualizar sensores em tempo real

setlocal
cd /d "%~dp0"

echo.
echo ============================================================================
echo   SafePlan - Dashboard de Monitoramento de Sensores
echo ============================================================================
echo.
echo Abrindo Dashboard...
echo Seu navegador abrira em: http://localhost:8501
echo.
echo Para parar, pressione CTRL+C nesta janela
echo.
pause

streamlit run app/main.py

endlocal
