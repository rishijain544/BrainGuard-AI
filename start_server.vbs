Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "d:\brain_tumour_prediction\backend"
objShell.Run "python -m uvicorn fastapi_backend:app --host 0.0.0.0 --port 8000", 1, False
