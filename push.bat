@echo off
rem =====================================================================
rem  push.bat - push with automatic fallback (direct <-> local proxy)
rem  Usage: push.bat [any extra git push args]
rem  NOTE: keep this file ASCII-only (cmd parses .bat with GBK).
rem =====================================================================
setlocal
cd /d "%~dp0"

echo [1/3] try current git config ...
git push %*
if not errorlevel 1 goto :done

echo [2/3] retry direct connection ...
git -c http.proxy= -c https.proxy= push %*
if not errorlevel 1 goto :done

echo [3/3] retry via local proxy 127.0.0.1:7897 ...
git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push %*
if not errorlevel 1 goto :done

echo [ERROR] push failed on all routes. Check network / proxy software.
pause
exit /b 1

:done
echo [OK] pushed.
git -c core.quotepath=false status -sb
pause
exit /b 0
