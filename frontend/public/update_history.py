with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add Date Filter and Export to CSV in the History controls
new_controls = '''<div class="history-controls" style="display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap;">
                <input type="text" id="hist-search" class="form-input" placeholder="Search Patient Name or ID..." style="flex: 1; min-width: 200px;">
                <input type="date" id="hist-date-filter" class="form-input" style="width: 180px;">
                <select id="hist-filter" class="form-select" style="width: 200px;">
                    <option value="all">All Results</option>
                    <option value="glioma">Glioma</option>
                    <option value="meningioma">Meningioma</option>
                    <option value="pituitary">Pituitary Tumor</option>
                    <option value="notumor">No Tumor</option>
                </select>
                <button class="btn btn-primary" id="export-csv-btn">
                    <svg viewBox="0 0 24 24" fill="none" style="width:16px;height:16px;margin-right:8px;"><path d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="currentColor" stroke-width="2"/></svg>
                    Export CSV
                </button>
            </div>'''

# Replace old controls
start = html.find('<div class="history-controls">')
if start == -1: start = html.find('<div class="history-controls"')
if start != -1:
    end = html.find('</div>', start) + 6
    html = html[:start] + new_controls + html[end:]

# Add Scan Details Modal
modal_html = '''
<!-- Scan Details Modal -->
<div id="scan-details-modal" class="modal hidden">
    <div class="modal-content" style="max-width: 800px;">
        <div class="modal-header">
            <h2>Scan Details</h2>
            <button id="close-details-btn" class="icon-btn"><svg viewBox="0 0 24 24" fill="none" style="width:24px;height:24px;"><path d="M6 18L18 6M6 6l12 12" stroke="currentColor" stroke-width="2"/></svg></button>
        </div>
        <div class="modal-body" id="scan-details-body">
            <!-- Content injected via JS -->
        </div>
    </div>
</div>
'''

if 'id="scan-details-modal"' not in html:
    html = html.replace('</body>', modal_html + '\n</body>')

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
