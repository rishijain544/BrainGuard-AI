import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

replacement = """
        const payload = {
            patient_name: document.getElementById('patient-name')?.value || 'Unknown Patient',
            patient_id: document.getElementById('patient-id')?.value || 'Unknown ID',
            age: document.getElementById('patient-age')?.value || 'N/A',
            scan_date: document.getElementById('scan-date')?.value || new Date().toISOString().split('T')[0],
"""

js = re.sub(
    r'const payload = \{\s*patient_name:\s*\'John Doe\',\s*patient_id:\s*\'PT-100\',\s*age:\s*45,\s*scan_date:\s*new Date\(\)\.toISOString\(\)\.split\(\'T\'\)\[0\],',
    replacement.strip(),
    js
)

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
