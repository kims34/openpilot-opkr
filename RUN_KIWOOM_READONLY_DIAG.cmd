@echo off
setlocal
cd /d "%~dp0"
REM Owner's already registered-IP Windows machine only; local env credentials required.
REM Read-only only. Nothing is installed or executed during unzip.
REM Prefer the active python selected by the shell/venv, so installed
REM packages match the interpreter used for the readonly diagnostic.
REM Fall back to the Python launcher only if python is not runnable.
python --version >nul 2>&1
if not errorlevel 1 (
  python -B kiwoom_readonly_route_compare.py
) else (
  py -3 -B kiwoom_readonly_route_compare.py
)
REM Preserve the probe exit status across informational echoes and pause.
REM A broker failure, missing credential or unsafe configuration is NOT a
REM successful Windows diagnostic process exit.
set "diagnostic_exit=%errorlevel%"
echo.
echo Read the assessment and stage/error codes above. Never share tokens or account IDs.
echo If dependencies are missing, install with the same Python selected above.
echo For python: python -m pip install -r kiwoom_readonly_pc_requirements.txt
echo For fallback: py -3 -m pip install -r kiwoom_readonly_pc_requirements.txt
pause
endlocal & exit /b %diagnostic_exit%
