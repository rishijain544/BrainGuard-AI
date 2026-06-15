import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('id="ui-export-btn-big" onclick="document.getElementById(\'download-pdf-btn\')?.click()" class=', 'id="ui-export-btn-big" class=')

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
