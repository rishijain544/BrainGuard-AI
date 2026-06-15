import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace scanHistory with brainguard_scan_history
js = js.replace("'scanHistory'", "'brainguard_scan_history'")
js = js.replace('"scanHistory"', "'brainguard_scan_history'")

# Replace s.ensemble_prediction with s.result.ensemble_prediction
# and s.ensemble_confidence with s.result.ensemble_confidence
# and s.models.cnn with s.result.models.cnn etc
# and s.patientName with s.patient.name, s.patientId with s.patient.id, s.patientAge with s.patient.age

replacements = {
    's.ensemble_prediction': 's.result.ensemble_prediction',
    's.ensemble_confidence': 's.result.ensemble_confidence',
    's.models': 's.result.models',
    's.patientName': 's.patient.name',
    's.patientId': 's.patient.id',
    's.patientAge': 's.patient.age',
    's.uncertainty': 's.result.uncertainty'
}

for old, new in replacements.items():
    js = js.replace(old, new)

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
