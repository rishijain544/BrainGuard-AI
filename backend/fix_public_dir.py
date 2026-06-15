import os
filepath = 'd:/brain_tumour_prediction/backend/fastapi_backend.py'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("PUBLIC_DIR = os.path.join(os.path.dirname(BASE_DIR), 'public')", "PUBLIC_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend', 'public')")

with open(filepath, 'w', encoding='utf-8') as f2:
    f2.write(text)
