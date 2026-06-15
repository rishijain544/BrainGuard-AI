import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the class attributes
html = re.sub(r'class="([^"]*)"\s+ml-72', r'class="\1 ml-72"', html)

# Fix the button
html = html.replace('id="ui-export-btn-big" class=', 'id="ui-export-btn-big" onclick="document.getElementById(\'download-pdf-btn\')?.click()" class=')

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
