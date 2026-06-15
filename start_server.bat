@echo off
cd /d d:\brain_tumour_prediction\backend
python -m uvicorn fastapi_backend:app --host 0.0.0.0 --port 8000
pause
