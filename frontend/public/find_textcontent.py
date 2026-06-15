import re

with open(r'd:\brain_tumour_prediction\frontend\public\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

lines = js.split('\n')
for i, line in enumerate(lines):
    if '.textContent' in line:
        print(f"{i+1}: {line.strip()}")
