import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

csv_logic = '''
    document.getElementById('export-csv-btn')?.addEventListener('click', () => {
        const history = loadHistory();
        if (history.length === 0) return alert('No history to export.');
        
        const headers = ['Patient Name', 'Patient ID', 'Age', 'Scan Date', 'Diagnosis', 'Confidence'];
        const rows = history.map(h => [
            h.patient.name, 
            h.patient.id, 
            h.patient.age, 
            h.patient.scanDate, 
            getDisplayName(h.result.ensemble_prediction), 
            (h.result.ensemble_confidence * 100).toFixed(1) + '%'
        ]);
        
        let csvContent = 'data:text/csv;charset=utf-8,' + headers.join(',') + '\\n' + rows.map(e => e.join(',')).join('\\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'patient_history.csv');
        document.body.appendChild(link);
        link.click();
    });
'''

idx = js.find("document.getElementById('clear-history-btn')")
if idx != -1:
    js = js[:idx] + csv_logic + '\n    ' + js[idx:]
    with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
