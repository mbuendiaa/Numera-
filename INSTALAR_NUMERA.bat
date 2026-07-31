@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo Instalando Numera
echo ========================================

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: No se encontro Python. Instala Python 3.10 o superior.
  pause
  exit /b 1
)
where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: No se encontro Node.js/npm. Instala Node.js 20 o superior.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  py -m venv backend\.venv
)
call backend\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -e backend
if errorlevel 1 goto :error

pushd frontend
call npm install
if errorlevel 1 goto :error
if not exist .env.local copy .env.example .env.local >nul
popd

echo.
echo Instalacion completada. Ejecuta INICIAR_NUMERA.bat
pause
exit /b 0

:error
echo.
echo ERROR durante la instalacion.
pause
exit /b 1
