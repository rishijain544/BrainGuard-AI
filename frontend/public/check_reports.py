import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'<main[^>]*id="page-reports"[^>]*>.*?</main>', html, re.DOTALL)
if m:
    print(m.group(0))
else:
    print('Not found')
