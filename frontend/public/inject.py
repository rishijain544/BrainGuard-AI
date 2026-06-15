with open('d:/brain_tumour_prediction/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_header = '<div class="header-controls">\n                <button id="settings-btn" class="nav-tab" style="padding: 6px 10px; margin-right: 12px;" title="Backend API Settings">⚙️</button>'

html = html.replace('<div class="header-controls">', new_header)

with open('d:/brain_tumour_prediction/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
