with open('d:/brain_tumour_prediction/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_section = '''<main id="page-analytics" class="page hidden">
        <!-- Current Scan Analytics -->
        <div class="current-scan-analytics hidden" id="current-scan-analytics">
            <h2 style="color: var(--text-primary); margin-bottom: 16px; font-family: var(--font-header);">Current Uploaded Scan Metrics</h2>
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-card-icon blue"><svg viewBox="0 0 24 24" fill="none"><path d="M4 4h16v16H4z" stroke="currentColor" stroke-width="2"/></svg></div>
                    <div><div id="ana-tumor-area" class="stat-card-value">-- mm²</div><div class="stat-card-label">Estimated Anomaly Area</div></div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon green"><svg viewBox="0 0 24 24" fill="none"><path d="M12 2v20M2 12h20" stroke="currentColor" stroke-width="2"/></svg></div>
                    <div><div id="ana-symmetry" class="stat-card-value">-- %</div><div class="stat-card-label">Brain Symmetry Index</div></div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon cyan"><svg viewBox="0 0 24 24" fill="none"><path d="M12 16v-4m0-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2"/></svg></div>
                    <div><div id="ana-mean-intensity" class="stat-card-value">--</div><div class="stat-card-label">Mean Pixel Intensity</div></div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-icon red"><svg viewBox="0 0 24 24" fill="none"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" stroke="currentColor" stroke-width="2"/></svg></div>
                    <div><div id="ana-lobe" class="stat-card-value">--</div><div class="stat-card-label">Image Focus</div></div>
                </div>
            </div>
            
            <div class="charts-row" style="margin-top: 24px; margin-bottom: 40px;">
                <div class="dashboard-card chart-card chart-card-wide" style="width: 100%;">
                    <div class="card-header"><h2>Pixel Intensity Distribution</h2><p>Grayscale histogram of the uploaded MRI</p></div>
                    <div class="card-body chart-body" style="height: 300px;">
                        <canvas id="chart-histogram"></canvas>
                    </div>
                </div>
            </div>
            
            <h2 style="color: var(--text-primary); margin-bottom: 16px; margin-top: 32px; font-family: var(--font-header);">Global Historical Aggregates</h2>
        </div>'''

html = html.replace('<main id="page-analytics" class="page hidden">', new_section)

with open('d:/brain_tumour_prediction/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
