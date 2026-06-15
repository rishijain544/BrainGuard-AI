modal = '''
    <!-- Settings Modal -->
    <div id="settings-modal" class="modal-overlay hidden">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Backend Connection Settings</h3>
                <button id="close-modal-btn" class="icon-btn">✖</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>API Server URL</label>
                    <input type="text" id="api-url-input" value="http://localhost:8000" placeholder="e.g., http://localhost:8000">
                </div>
                <div style="margin-top: 16px; display: flex; justify-content: space-between; align-items: center;">
                    <span id="modal-test-status" class="test-badge">UNTESTED</span>
                    <button id="save-settings-btn" class="primary-btn">Save & Reconnect</button>
                </div>
            </div>
        </div>
    </div>
'''

with open('d:/brain_tumour_prediction/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<script src="app.js"></script>', modal + '\n    <script src="app.js"></script>')

with open('d:/brain_tumour_prediction/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
