import re

with open(r'd:\brain_tumour_prediction\frontend\public\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

s = js.find("function displayAnalysisResults")
if s != -1:
    # Just print the first 100 lines of this function
    e = s
    for i in range(100):
        e = js.find('\n', e + 1)
        if e == -1: break
    print(js[s:e])
