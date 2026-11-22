@echo off
rem =====================================================================
rem  课设二启动脚本：编译 -> 启动本地服务 -> 自动打开浏览器
rem  零第三方依赖，验收现场双击本文件即可运行。
rem =====================================================================
setlocal
cd /d "%~dp0"

rem --- 定位 JDK：优先用环境变量，找不到则回退到已知安装位置 ---
if not defined JAVA_HOME set "JAVA_HOME=C:\Program Files\Microsoft\jdk-25.0.5.102-hotspot"
if not exist "%JAVA_HOME%\bin\javac.exe" (
    echo [ERROR] 找不到 JDK，请检查 JAVA_HOME 环境变量：%JAVA_HOME%
    pause
    exit /b 1
)

if not exist out\classes mkdir out\classes

echo [1/2] 编译中 ...
"%JAVA_HOME%\bin\javac.exe" -encoding UTF-8 -d out\classes src\rpn\*.java
if errorlevel 1 (
    echo [ERROR] 编译失败，请查看上面的报错。
    pause
    exit /b 1
)

echo [2/2] 启动服务 http://127.0.0.1:8080 ...
start "" http://127.0.0.1:8080
"%JAVA_HOME%\bin\java.exe" -cp out\classes rpn.Main

echo 服务已退出。
pause
