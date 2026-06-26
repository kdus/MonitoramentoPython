@echo off
setlocal

set SERVICE_NAME=MonitoramentoPython
set TASK_NAME=Ptytho - MonitoramentoViaweb
set SCRIPT_DIR=%~dp0
set TARGET_APP=%SCRIPT_DIR%main.py

::: Verifica admin
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Execute este script como Administrador.
    pause
    exit /b 1
)

echo.
echo Parando tarefa agendada %TASK_NAME% (se existir)...
schtasks /end /tn "%TASK_NAME%" >nul 2>&1

echo Removendo tarefa agendada %TASK_NAME% (se existir)...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

echo.
echo Encerrando processos Python do MonitoramentoPython (se existir)...
powershell -NoProfile -Command ^
  "$dir = (Resolve-Path -LiteralPath '%SCRIPT_DIR%' -ErrorAction SilentlyContinue).Path; " ^
  "if (-not $dir) { exit 0 } " ^
  "$main = (Join-Path $dir 'main.py'); " ^
  "$bat  = (Join-Path $dir 'iniciar.bat'); " ^
  "$rx = [Regex]::Escape($main) + '|' + [Regex]::Escape($bat); " ^
  "$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and ($_.Name -in @('python.exe','pythonw.exe','py.exe','cmd.exe')) -and ($_.CommandLine -match $rx) }; " ^
  "foreach ($p in $procs) { try { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue } catch {} }"

echo.
echo Parando servico %SERVICE_NAME% (legado, se existir)...
sc stop %SERVICE_NAME% >nul 2>&1
timeout /t 3 /nobreak >nul

echo Removendo servico %SERVICE_NAME% (legado, se existir)...
sc delete %SERVICE_NAME% >nul 2>&1

echo.
echo Remocao concluida.
echo.
pause

