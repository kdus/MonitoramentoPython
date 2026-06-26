@echo off
REM ********************************************************************************************************
REM * Empresa        : SI Sistemas Inteligentes
REM * Script         : START_HERE.bat
REM * Objetivo       : Iniciar TUDO - Monitoramento + Dashboard
REM * Data Criacao   : 27/01/2026
REM ********************************************************************************************************

title VIAWEB Receiver - Inicializador Completo
color 0A

echo.
echo ================================================================================
echo.
echo    ██╗   ██╗██╗ █████╗ ██╗    ██╗███████╗██████╗ 
echo    ██║   ██║██║██╔══██╗██║    ██║██╔════╝██╔══██╗
echo    ██║   ██║██║███████║██║ █╗ ██║█████╗  ██████╔╝
echo    ╚██╗ ██╔╝██║██╔══██║██║███╗██║██╔══╝  ██╔══██╗
echo     ╚████╔╝ ██║██║  ██║╚███╔███╔╝███████╗██████╔╝
echo      ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚═════╝ 
echo.
echo    VIAWEB Receiver - Sistema de Monitoramento
echo    SI Sistemas Inteligentes Eletronicos
echo.
echo ================================================================================
echo.

REM Muda para o diretorio do script
cd /d "%~dp0"

echo [Inicializador] Verificando configuracao...
echo.

REM Verifica se o arquivo .env existe
if not exist ".env" (
    echo [ERRO] Arquivo .env nao encontrado!
    echo.
    echo Por favor, copie o arquivo .env.example para .env e configure-o.
    echo.
    pause
    exit /b 1
)

echo [OK] Arquivo .env encontrado
echo.

REM Menu de opcoes
echo Escolha uma opcao:
echo.
echo   [1] Iniciar TUDO (Monitoramento + Dashboard)
echo   [2] Iniciar apenas Monitoramento (main.py)
echo   [3] Iniciar apenas Dashboard (web)
echo   [4] Testar conexao com banco de dados
echo   [5] Sair
echo.

set /p opcao="Digite o numero da opcao: "

if "%opcao%"=="1" goto iniciar_tudo
if "%opcao%"=="2" goto iniciar_monitoramento
if "%opcao%"=="3" goto iniciar_dashboard
if "%opcao%"=="4" goto testar_db
if "%opcao%"=="5" goto sair

echo.
echo [ERRO] Opcao invalida!
pause
goto sair

:iniciar_tudo
echo.
echo ================================================================================
echo   INICIANDO SISTEMA COMPLETO
echo ================================================================================
echo.
echo [Inicializador] Abrindo terminal para Monitoramento...
start "VIAWEB Monitoramento" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo [Inicializador] Abrindo terminal para Dashboard...
start "VIAWEB Dashboard" cmd /k "python run_dashboard.py"
timeout /t 2 /nobreak >nul

echo [Inicializador] Abrindo navegador...
timeout /t 3 /nobreak >nul
start http://localhost:5000

echo.
echo ================================================================================
echo   SISTEMA COMPLETO INICIADO COM SUCESSO!
echo ================================================================================
echo.
echo   Terminal 1: Monitoramento (main.py) - Recebendo eventos
echo   Terminal 2: Dashboard (web)         - Interface web
echo   Navegador:  http://localhost:5000   - Visualizacao
echo.
echo   Pressione qualquer tecla para voltar ao menu...
echo ================================================================================
pause >nul
goto sair

:iniciar_monitoramento
echo.
echo ================================================================================
echo   INICIANDO MONITORAMENTO
echo ================================================================================
echo.
python main.py
goto sair

:iniciar_dashboard
echo.
echo ================================================================================
echo   INICIANDO DASHBOARD WEB
echo ================================================================================
echo.
python run_dashboard.py
goto sair

:testar_db
echo.
echo ================================================================================
echo   TESTANDO CONEXAO COM BANCO DE DADOS
echo ================================================================================
echo.
python -c "from dotenv import load_dotenv; import os; load_dotenv(); from services.database_service import DatabaseService; db = DatabaseService(); print('[Teste] Conectando...'); print('[OK] Conectado!' if db.connect() else '[ERRO] Falha na conexao'); db.disconnect()"
echo.
pause
goto sair

:sair
echo.
echo [Inicializador] Encerrando...
exit /b 0
