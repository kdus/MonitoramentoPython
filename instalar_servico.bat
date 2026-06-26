@echo off
setlocal EnableExtensions

::: ====================================================================
:::  MonitoramentoPython - Instalar como "servico" resiliente no Windows
:::  ESTRATEGIA: Tarefa Agendada (SYSTEM no boot) chamando iniciar.bat (watchdog)
:::  Motivo: sc.exe com python.exe nao implementa Service Control Manager (SCM)
:::          e pode ficar instavel em VM/suspensao/desconexao.
::: ====================================================================

set TASK_NAME=Ptytho - MonitoramentoViaweb
set SCRIPT_DIR=%~dp0
set TASK_XML_TEMPLATE=%SCRIPT_DIR%MonitoramentoPython_task.xml
set TASK_XML_RENDERED=%TEMP%\MonitoramentoPython_task_rendered.xml

::: Verifica admin
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Execute este script como Administrador.
    echo        Clique com botao direito ^> Executar como administrador.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo  Instalando: %TASK_NAME% (Tarefa Agendada / SYSTEM / no boot)
echo  Template XML: %TASK_XML_TEMPLATE%
echo  Acao: iniciar.bat (watchdog, reinicia se cair)
echo ====================================================================
echo.

if not exist "%TASK_XML_TEMPLATE%" (
    echo [ERRO] Arquivo XML nao encontrado: %TASK_XML_TEMPLATE%
    echo       Verifique se o projeto foi extraido completo.
    pause
    exit /b 1
)

::: (Opcional) Evita suspensao no modo AC (VM costuma ficar em "energia")
powercfg /change standby-timeout-ac 0 >nul 2>&1
powercfg /change hibernate-timeout-ac 0 >nul 2>&1

::: Remove tarefa antiga se existir
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

::: Renderiza o XML substituindo __SCRIPT_DIR__ pelo caminho real do projeto
powershell -NoProfile -Command ^
  "$src='%TASK_XML_TEMPLATE%'; $dst='%TASK_XML_RENDERED%'; $dir='%SCRIPT_DIR%';" ^
  "$xml=[IO.File]::ReadAllText($src); $xml=$xml.Replace('__SCRIPT_DIR__',$dir);" ^
  "[IO.File]::WriteAllText($dst,$xml,[Text.Encoding]::Unicode)"

if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao renderizar XML no caminho: %TASK_XML_RENDERED%
    pause
    exit /b 1
)

::: Cria a tarefa via XML (SYSTEM + boot trigger + restart on failure)
schtasks /create /tn "%TASK_NAME%" /xml "%TASK_XML_RENDERED%" /f
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao criar a Tarefa Agendada.
    echo        Verifique se o XML esta valido e tente novamente.
    pause
    exit /b 1
)

::: Executa imediatamente (sem esperar reboot)
schtasks /run /tn "%TASK_NAME%" >nul 2>&1

echo.
echo ====================================================================
echo  Instalado com sucesso!
echo  Nome: %TASK_NAME%
echo  Status: schtasks /query /tn "%TASK_NAME%" /v /fo list
echo  Parar:  schtasks /end   /tn "%TASK_NAME%"
echo  Iniciar: schtasks /run  /tn "%TASK_NAME%"
echo  Remover: desinstalar_servico.bat
echo  Log: %SCRIPT_DIR%logs\Ptytho-MonitoramentoViaweb.log
echo ====================================================================
echo.

pause

