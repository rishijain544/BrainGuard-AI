import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'(class="page hidden pt-24 px-gutter")\s+(id="page-analytics")', r'\1 ml-72 \2', html)
html = re.sub(r'(class="page hidden pt-24 px-gutter")\s+(id="page-history")', r'\1 ml-72 \2', html)
html = re.sub(r'(class="page hidden")\s+(id="page-reports")', r'\1 ml-72 \2', html)
html = re.sub(r'(class="page hidden dashboard-wrapper")\s+(id="page-about")', r'\1 ml-72 \2', html)
html = re.sub(r'(class="page hidden dashboard-wrapper")\s+(id="page-contact")', r'\1 ml-72 \2', html)

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
