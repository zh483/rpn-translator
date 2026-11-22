@echo off
rem =====================================================================
rem  Course design 2 launcher: compile -> start local server -> open browser
rem  NOTE: keep this file ASCII-only. cmd.exe parses .bat with the OEM
rem        code page (GBK on zh-CN Windows); UTF-8 Chinese breaks parsing.
rem =====================================================================
setlocal
cd /d "%~dp0"

rem --- locate JDK: prefer JAVA_HOME, fall back to known install path ---
if not exist "%JAVA_HOME%\bin\javac.exe" (
    if exist "C:\Program Files\Microsoft\jdk-25.0.5.102-hotspot\bin\javac.exe" (
        set "JAVA_HOME=C:\Program Files\Microsoft\jdk-25.0.5.102-hotspot"
    )
)
if not exist "%JAVA_HOME%\bin\javac.exe" (
    echo [ERROR] JDK not found. Please check JAVA_HOME: %JAVA_HOME%
    pause
    exit /b 1
)

if not exist out\classes mkdir out\classes

rem --- friendly message when there is no source yet ---
dir /b src\rpn\*.java >nul 2>&1
if errorlevel 1 (
    echo [INFO] No .java files under src\rpn yet.
    echo        Create Token / TokenType / CompileException / Lexer first,
    echo        see the Day01 task card under docs\
    pause
    exit /b 0
)

echo [1/2] Compiling ...
"%JAVA_HOME%\bin\javac.exe" -encoding UTF-8 -d out\classes src\rpn\*.java
if errorlevel 1 (
    echo [ERROR] Compilation failed. See messages above.
    pause
    exit /b 1
)

echo [2/2] Starting server at http://127.0.0.1:8080 ...
start "" http://127.0.0.1:8080
"%JAVA_HOME%\bin\java.exe" -cp out\classes rpn.Main

echo Server stopped.
pause
