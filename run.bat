@echo off
REM === Activar entorno virtual si existe ===
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM === Ejecutar la aplicación en localhost ===
python -m uvicorn src.main:get_app --host 127.0.0.1 --port 8000 --factory

REM === Mantener la ventana abierta si hubo error ===
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La aplicación no se pudo iniciar.
    echo Verifica que hayas instalado dependencias con:
    echo     pip install -r requirements.txt
    pause
)

