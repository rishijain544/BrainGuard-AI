import re

with open(r'd:\brain_tumour_prediction\frontend\public\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

variables = ['gaugeValue', 'statusBadge', 'diagBadge', 'statAgreement', 'statUncertainty', 'statCi', 'recTitle', 'recAction', 'opacityPct', 'predEl', 'confEl', 'btnText']
for var in variables:
    matches = re.findall(f'.{{0,30}}{var}.{{0,30}}', js)
    for m in matches[:2]:
        print(m.strip())
