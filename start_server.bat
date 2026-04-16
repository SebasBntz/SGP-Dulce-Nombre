@echo off
echo Iniciando el servidor de Parroquia...
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
