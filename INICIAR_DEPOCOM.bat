
@echo off
title DepoCom UHO - Iniciador
cd /d "%~dp0"

echo ==========================================
echo       INICIANDO DEPOCOM UHO
echo ==========================================
echo.

if not exist "backend\.venv\Scripts\python.exe" (
    echo ERROR: No se encontro el entorno Python.
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ERROR: No se encontro el frontend.
    pause
    exit /b 1
)

echo Iniciando Django...
start "DepoCom - Django" cmd /k "cd /d ""%~dp0backend"" && .venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

echo Iniciando Vue...
start "DepoCom - Vue" cmd /k "cd /d ""%~dp0frontend"" && npm.cmd run dev"

echo.
echo Se abrieron dos ventanas:
echo   1. Backend Django
echo   2. Frontend Vue
echo.
echo Espera a que ambos servidores indiquen
echo que estan funcionando.
echo.
echo Luego abre:
echo http://localhost:5173/
echo.

pause
