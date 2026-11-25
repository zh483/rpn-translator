@echo off
rem =====================================================================
rem  Course design 2 launcher: compile -> launch Swing desktop UI
rem  NOTE: keep this file ASCII-only (cmd parses .bat with the OEM code
rem        page; UTF-8 Chinese breaks parsing).
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

echo [2/2] Launching desktop UI ...
"%JAVA_HOME%\bin\java.exe" -cp out\classes rpn.Main

echo Application closed.
pause
