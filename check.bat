@echo off
rem =====================================================================
rem  Project gate: run before every commit.
rem  Any FAIL means: do not commit, do not move to the next day.
rem =====================================================================
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if %errorlevel%==0 (
    py -3.13 tools\check_project.py
) else (
    python tools\check_project.py
)

pause
