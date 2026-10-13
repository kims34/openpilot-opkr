@echo off
setlocal
cd /d "%~dp0"
REM Local owner's registered-IP Windows machine only. Reads existing env credentials.
REM No orders are sent. Nothing runs during extraction; user must launch this script.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 -B kiwoom_readonly_route_compare.py
) else (
  python -B kiwoom_readonly_route_compare.py
)
echo.
echo Only share assessment, STAGE, RETURN_CODE, DETAIL_CODE; never disclose private keys or account.
echo If missing dependencies, install with: py -3 -m pip install -r kiwoom_readonly_pc_requirements.txt
pause
endlocal
