@echo off
REM ********************************************************************************************************
REM * Empresa        : SI Sistemas Inteligentes
REM * Script         : iniciar.bat
REM * Objetivo       : Script para iniciar o monitoramento do VIAWEB Receiver
REM * Data Criacao   : 27/01/2026
REM ********************************************************************************************************

setlocal EnableExtensions EnableDelayedExpansion

REM Garante UTF-8 para prints com acentos no Windows
chcp 65001 >nul 2>&1

set APP_TITLE=Ptytho - MonitoramentoViaweb
set SCRIPT_DIR=%~dp0
set LOG_DIR=%SCRIPT_DIR%logs
set LOG_FILE=%LOG_DIR%\Ptytho-MonitoramentoViaweb.log
set VENV_ACTIVATE=%SCRIPT_DIR%venv\Scripts\activate.bat

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

echo ================================================================================
echo    %APP_TITLE%
echo    Iniciando aplicacao (watchdog 24/7)...
echo    Log: %LOG_FILE%
echo ================================================================================
echo.

REM Muda para o diretorio do script
cd /d "%SCRIPT_DIR%"

REM Ativa o ambiente virtual se existir
if exist "%VENV_ACTIVATE%" (
    echo [Iniciar] Ativando ambiente virtual...
    call "%VENV_ACTIVATE%"
)

REM Argumentos:
REM   --once  : executa apenas uma vez (sem reinicio)
REM   (padrao): reinicia se o processo encerrar
set RUN_ONCE=0
if /I "%~1"=="--once" set RUN_ONCE=1

:loop
for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd HH:mm:ss\""') do set TS=%%I
echo [%TS%] [Iniciar] Executando main.py...>> "%LOG_FILE%"

REM Executa o programa principal (sem buffer de saida), redirecionando stdout/stderr para log
python -u "%SCRIPT_DIR%main.py" >> "%LOG_FILE%" 2>&1
set EXIT_CODE=%ERRORLEVEL%

for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd HH:mm:ss\""') do set TS=%%I
echo [%TS%] [Iniciar] main.py finalizou. ExitCode=!EXIT_CODE!>> "%LOG_FILE%"

if "%RUN_ONCE%"=="1" goto :eof

REM Pequena pausa antes de reiniciar
timeout /t 5 /nobreak >nul
goto loop
