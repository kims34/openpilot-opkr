@echo off
setlocal
cd /d "%~dp0"
REM Owner's already registered-IP Windows machine only; local env credentials required.
REM Read-only only. Nothing is installed or executed during unzip.
py -3 --version >nul 2>&1
if not errorlevel 1 (
  py -3 -B kiwoom_readonly_route_compare.py
) else (
  python -B kiwoom_readonly_route_compare.py
)
echo.
echo Read the assessment and stage/error codes above. Never share tokens or account IDs.
echo If dependencies are missing: python -m pip install -r kiwoom_readonly_pc_requirements.txt
pause
endlocal
