import re

with open(r'd:\brain_tumour_prediction\frontend\public\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

s = js.find("analyzeBtn.addEventListener('click',")
if s != -1:
    e = js.find("});", s)
    print(js[s:e+3])
