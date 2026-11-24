@echo off
REM Layer B supervisor for Windows. Run from the project folder. Stop: create state\STOP_SUPERVISOR
cd /d %~dp0\..
if not exist logs mkdir logs
set BACKOFF=300
:loop
if exist state\STOP_SUPERVISOR goto end
findstr /C:"\"FINISHED\"" state\agent_state.json >nul && goto end
echo [%date% %time%] launching agent >> logs\supervisor.log
pushd ..
set /p PROMPT=<project\BOOTSTRAP_PROMPT.txt
claude -p "%PROMPT%" --permission-mode acceptEdits >> project\logs\agent_run_win.log 2>&1
popd
echo [%date% %time%] agent exited, sleeping %BACKOFF%s >> logs\supervisor.log
timeout /t %BACKOFF% /nobreak >nul
if %BACKOFF%==300 (set BACKOFF=900) else if %BACKOFF%==900 (set BACKOFF=1800) else (set BACKOFF=3600)
goto loop
:end
echo [%date% %time%] supervisor exit >> logs\supervisor.log
