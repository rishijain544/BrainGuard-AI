import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<button class="mb-8 w-full bg-primary-container', '<button id="new-scan-btn" class="mb-8 w-full bg-primary-container')

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
