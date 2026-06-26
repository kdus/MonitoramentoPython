@echo off
REM ********************************************************************************************************
REM * Empresa        : SI Sistemas Inteligentes
REM * Script         : iniciar_dashboard.bat
REM * Objetivo       : Script para iniciar o dashboard web
REM * Data Criacao   : 27/01/2026
REM ********************************************************************************************************

echo ================================================================================
echo    VIAWEB Receiver - Dashboard Web
echo    Iniciando servidor...
echo ================================================================================
echo.

REM Muda para o diretorio do script
cd /d "%~dp0"

REM Ativa o ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo [Dashboard] Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Executa o servidor web
echo [Dashboard] Iniciando servidor web na porta 5000...
echo [Dashboard] Acesse: http://localhost:5000
echo.
python run_dashboard.py

echo.
echo [Dashboard] Servidor encerrado.
pause
