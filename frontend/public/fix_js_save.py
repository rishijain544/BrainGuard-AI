import re

filepath = 'd:/brain_tumour_prediction/frontend/public/app.js'
with open(filepath, 'r', encoding='utf-8') as f:
    js = f.read()

# We want to add localStorage saving inside analyzeScan, right after data is returned successfully.
# Look for: displayAnalysisResults(data);
save_logic = '''
            // Save to localStorage
            const scans = JSON.parse(localStorage.getItem('scanHistory') || '[]');
            // add patient data to data object
            data.patientName = document.getElementById('patient-name')?.value || 'Unknown';
            data.patientId = document.getElementById('patient-id')?.value || 'Unknown';
            data.patientAge = document.getElementById('patient-age')?.value || 'Unknown';
            data.timestamp = new Date().toISOString();
            scans.push(data);
            localStorage.setItem('scanHistory', JSON.stringify(scans));
            
            // Update UI
            updateAnalyticsPage();
            updateHistoryPage();
            
            displayAnalysisResults(data);
'''

# Wait, `displayAnalysisResults(data)` might occur multiple times. Let's find it inside the fetch block.
if 'localStorage.setItem(\'scanHistory\'' not in js:
    # find where displayAnalysisResults(data) is called after fetch
    js = js.replace('displayAnalysisResults(data);', save_logic, 1)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(js)
