@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Genera el instalador .exe con jpackage (requiere JDK 17+ y WiX Toolset). Ejecutar desde avance_4\jpackage
if exist build rmdir /s /q build
if exist salida rmdir /s /q salida
mkdir build\clases build\entrada\proyecto salida
javac -d build\clases src\Lanzador.java
jar --create --file build\entrada\lanzador.jar --main-class Lanzador -C build\clases .
xcopy ..\app.py build\entrada\proyecto\ /Y >nul
xcopy ..\main.py build\entrada\proyecto\ /Y >nul
xcopy ..\requirements.txt build\entrada\proyecto\ /Y >nul
xcopy ..\src build\entrada\proyecto\src\ /E /I /Y >nul
xcopy ..\interfaz build\entrada\proyecto\interfaz\ /E /I /Y >nul
xcopy ..\datos build\entrada\proyecto\datos\ /E /I /Y >nul
xcopy ..\resultados build\entrada\proyecto\resultados\ /E /I /Y >nul
jpackage --type exe --win-shortcut --win-menu --name DashboardClimatico --app-version 1.0 --vendor "Parra, Carrillo, Leiva" --input build\entrada --main-jar lanzador.jar --main-class Lanzador --dest salida
if errorlevel 1 (echo HUBO UN ERROR, revise arriba) else (echo Listo)
pause
