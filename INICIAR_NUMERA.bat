@echo off
setlocal
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
  echo Numera no esta instalado. Ejecutando instalacion...
  call INSTALAR_NUMERA.bat
  if errorlevel 1 exit /b 1
)
if not exist "frontend\node_modules" (
  echo Faltan dependencias del frontend. Ejecutando instalacion...
  call INSTALAR_NUMERA.bat
  if errorlevel 1 exit /b 1
)
if not exist "frontend\.env.local" copy "frontend\.env.example" "frontend\.env.local" >nul

start "Numera Backend" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn numera.main:app --app-dir src --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul
start "Numera Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo Numera se ha iniciado. Se han abierto backend y frontend automaticamente.
exit /b 0
