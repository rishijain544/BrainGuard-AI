import re

with open(r'd:\brain_tumour_prediction\frontend\public\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# find analyzeBtn usage
analyze_matches = re.finditer(r'.{0,100}analyzeBtn.{0,100}', js)
for m in analyze_matches:
    print(m.group(0))

