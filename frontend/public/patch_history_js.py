import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update renderHistory logic to include Date filter and new buttons
history_logic = '''
    // ──────────────────────────────────────────────────────────────────────────
    // HISTORY ACTIONS (EXPORT, DELETE, VIEW)
    // ──────────────────────────────────────────────────────────────────────────
    window.deleteHistoryItem = function(id) {
        if (!confirm('Are you sure you want to delete this scan record?')) return;
        let history = loadHistory();
        history = history.filter(item => item.id !== id);
        saveHistory(history);
        renderHistory();
        if (document.getElementById('page-analytics').classList.contains('active')) renderAnalytics();
    };

    window.viewHistoryItem = function(id) {
        const history = loadHistory();
        const item = history.find(i => i.id === id);
        if (!item) return;
        
        const modal = document.getElementById('scan-details-modal');
        const body = document.getElementById('scan-details-body');
        
        body.innerHTML = `
            <div style="display: flex; gap: 24px; margin-bottom: 24px;">
                <div style="flex: 1;">
                    <h3 style="color: var(--accent-blue); margin-bottom: 12px;">Patient Information</h3>
                    <p><strong>Name:</strong> ${item.patient.name}</p>
                    <p><strong>ID:</strong> ${item.patient.id}</p>
                    <p><strong>Age:</strong> ${item.patient.age}</p>
                    <p><strong>Date:</strong> ${item.patient.scanDate}</p>
                </div>
                <div style="flex: 1;">
                    <h3 style="color: var(--color-warning); margin-bottom: 12px;">AI Diagnosis</h3>
                    <p><strong>Prediction:</strong> <span style="text-transform: capitalize;">${item.result.ensemble_prediction || 'N/A'}</span></p>
                    <p><strong>Confidence:</strong> ${(item.result.ensemble_confidence * 100).toFixed(1)}%</p>
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
    };

    document.getElementById('close-details-btn')?.addEventListener('click', () => {
        document.getElementById('scan-details-modal').classList.add('hidden');
    });

    document.getElementById('export-csv-btn')?.addEventListener('click', () => {
        const history = loadHistory();
        if (history.length === 0) return alert('No data to export.');
        
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += "ID,Date,Patient Name,Patient ID,Age,Diagnosis,Confidence\\n";
        
        history.forEach(item => {
            const row = [
                item.id,
                item.patient.scanDate,
                `"${item.patient.name}"`,
                item.patient.id,
                item.patient.age,
                item.result.ensemble_prediction,
                item.result.ensemble_confidence
            ].join(",");
            csvContent += row + "\\n";
        });
        
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "brainguard_history.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // Handle date filter
    document.getElementById('hist-date-filter')?.addEventListener('change', renderHistory);
'''

# We need to inject the actions code
if 'window.deleteHistoryItem = function' not in js:
    js = js.replace('function renderHistory() {', history_logic + '\n    function renderHistory() {')

# Now patch the filtering logic in renderHistory
filter_patch = '''
        const dateFilter  = document.getElementById('hist-date-filter')?.value;

        // Filter
        const filtered = history.filter(entry => {
            const matchSearch = !search ||
                entry.patient.name.toLowerCase().includes(search) ||
                entry.patient.id.toLowerCase().includes(search);
            const matchFilter = filterType === 'all' || entry.result.ensemble_prediction === filterType;
            const matchDate   = !dateFilter || entry.patient.scanDate === dateFilter;
            return matchSearch && matchFilter && matchDate;
        });
'''
js = re.sub(r'// Filter.*?}\);', filter_patch.strip(), js, flags=re.DOTALL)


# Now patch the row generation inside renderHistory
row_replacement = '''
            const tr = document.createElement('tr');
            const conf = (e.result.ensemble_confidence * 100).toFixed(1);
            let badge = '';
            if (e.result.ensemble_prediction === 'notumor') badge = `<span class="badge badge-green">No Tumor</span>`;
            else badge = `<span class="badge badge-red" style="text-transform:capitalize;">${e.result.ensemble_prediction}</span>`;
            
            tr.innerHTML = `
                <td>${e.patient.scanDate}</td>
                <td>
                    <div style="font-weight: 600;">${e.patient.name}</div>
                    <div style="font-size: 11px; color: var(--text-secondary);">ID: ${e.patient.id}</div>
                </td>
                <td>${badge}</td>
                <td>
                    <div class="conf-bar"><div class="conf-fill" style="width: ${conf}%;"></div></div>
                    <div style="font-size: 11px; margin-top: 4px; text-align: right;">${conf}%</div>
                </td>
                <td>
                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 12px; margin-right: 4px;" onclick="viewHistoryItem(${e.id})">View</button>
                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 12px; color: #ef4444; border-color: #ef4444;" onclick="deleteHistoryItem(${e.id})">Del</button>
                </td>
            `;
'''
js = re.sub(r'const tr = document\.createElement.*?`;', row_replacement.strip(), js, flags=re.DOTALL)

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
