@echo off
cd /d "%~dp0backend"
python -m pip install -e .
cd /d "%~dp0frontend"
call npm install
echo.
echo Instalacion completada. A partir de ahora abre START_NUMERA.vbs
pause
