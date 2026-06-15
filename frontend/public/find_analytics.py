import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print('Analytics match:', html.find('id="page-analytics"'))
