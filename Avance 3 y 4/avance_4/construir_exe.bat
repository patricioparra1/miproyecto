@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Generando DashboardClimatico.exe ===
set PY=
where python >nul 2>&1 && set PY=python
if "%PY%"=="" (where py >nul 2>&1 && set PY=py)
if "%PY%"=="" (
  echo Python no esta instalado. Intentando instalarlo con winget...
  winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
  echo.
  echo Cierre esta ventana y vuelva a abrir construir_exe.bat para continuar.
  pause
  exit /b 1
)
%PY% -m pip install -r requirements.txt pyinstaller || goto error
if not exist datos\procesados\dataset_limpio.csv (%PY% main.py || goto error)
%PY% -m PyInstaller --noconfirm --onefile --name DashboardClimatico --add-data "interfaz;interfaz" --add-data "datos/procesados;datos/procesados" app.py || goto error
copy /Y dist\DashboardClimatico.exe DashboardClimatico.exe >nul
echo.
echo LISTO: DashboardClimatico.exe esta en esta misma carpeta.
explorer .
pause
exit /b 0
:error
echo.
echo HUBO UN ERROR, revise los mensajes de arriba.
pause
exit /b 1
