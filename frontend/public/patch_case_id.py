import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

replacement = """
        // PDF Data caching
        window.currentPrediction = data;
        const pid = document.getElementById('patient-id')?.value || 'Pending';
        const caseEl = document.getElementById('ui-case-id');
        if (caseEl) caseEl.textContent = `Case #${pid}`;
"""

js = js.replace('// PDF Data caching\n        window.currentPrediction = data;', replacement.strip())

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
