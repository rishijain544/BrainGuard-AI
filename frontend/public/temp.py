import re

with open(r'd:\brain_tumour_prediction\frontend\public\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# find file-input
file_input_matches = re.finditer(r'.{0,50}file-input.{0,100}', js)
for m in file_input_matches:
    print(m.group(0))

# find /predict
predict_matches = re.finditer(r'.{0,100}/predict.{0,100}', js)
for m in predict_matches:
    print(m.group(0))
