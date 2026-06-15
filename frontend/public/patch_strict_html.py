import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Analytics Page Replacement
new_analytics = '''<main class="page hidden pt-24 px-gutter" id="page-analytics">
    <div class="mb-8">
        <h2 class="text-headline-lg font-bold text-primary-fixed tracking-tight">Analytics Dashboard</h2>
        <p class="text-body-sm text-on-surface-variant">Global performance metrics across all scans</p>
    </div>

    <!-- Analytics Stats Row -->
    <div class="grid grid-cols-4 gap-4 mb-8">
        <div class="glass-panel p-4 rounded-xl border-l-4 border-primary">
            <div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Total Scans</div>
            <div class="text-headline-lg font-bold text-on-surface" id="ana-total-scans">0</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border-l-4 border-error">
            <div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Tumors Detected</div>
            <div class="text-headline-lg font-bold text-error" id="ana-tumor-count">0</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border-l-4 border-green-400">
            <div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">No Tumor Cases</div>
            <div class="text-headline-lg font-bold text-green-400" id="ana-clear-count">0</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border-l-4 border-secondary">
            <div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Average Confidence</div>
            <div class="text-headline-lg font-bold text-secondary" id="ana-avg-conf">—</div>
        </div>
    </div>

    <!-- Charts Grid -->
    <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="glass-panel p-6 rounded-2xl">
            <h3 class="font-bold text-on-surface mb-4">Tumor Distribution</h3>
            <div class="relative h-64 w-full flex items-center justify-center">
                <div class="text-on-surface-variant hidden" id="ana-no-data-pie">No scan data available</div>
                <canvas id="chart-pie"></canvas>
            </div>
        </div>
        <div class="glass-panel p-6 rounded-2xl">
            <h3 class="font-bold text-on-surface mb-4">Scan Activity Trend</h3>
            <div class="relative h-64 w-full flex items-center justify-center">
                <div class="text-on-surface-variant hidden" id="ana-no-data-line">No scan data available</div>
                <canvas id="chart-line"></canvas>
            </div>
        </div>
        <div class="glass-panel p-6 rounded-2xl">
            <h3 class="font-bold text-on-surface mb-4">Model Performance</h3>
            <div class="relative h-64 w-full flex items-center justify-center">
                <div class="text-on-surface-variant hidden" id="ana-no-data-bar">No scan data available</div>
                <canvas id="chart-bar"></canvas>
            </div>
        </div>
        <div class="glass-panel p-6 rounded-2xl">
            <h3 class="font-bold text-on-surface mb-4">Confidence Trend</h3>
            <div class="relative h-64 w-full flex items-center justify-center">
                <div class="text-on-surface-variant hidden" id="ana-no-data-trend">No scan data available</div>
                <canvas id="chart-trend"></canvas>
            </div>
        </div>
    </div>

    <!-- Recent Predictions Table -->
    <div class="glass-panel p-6 rounded-2xl mb-8">
        <h3 class="font-bold text-on-surface mb-4">Recent Predictions</h3>
        <div class="w-full overflow-x-auto">
            <table class="w-full text-left border-collapse" id="ana-recent-table">
                <thead>
                    <tr class="border-b border-white/10 text-on-surface-variant text-[12px] uppercase tracking-wider">
                        <th class="py-3 px-4 font-bold">Patient</th>
                        <th class="py-3 px-4 font-bold">Diagnosis</th>
                        <th class="py-3 px-4 font-bold">Confidence</th>
                        <th class="py-3 px-4 font-bold">Date</th>
                    </tr>
                </thead>
                <tbody id="ana-recent-tbody" class="text-body-sm text-on-surface">
                    <!-- Populated by JS -->
                </tbody>
            </table>
            <div class="text-center py-8 text-on-surface-variant hidden" id="ana-recent-empty">No recent predictions found.</div>
        </div>
    </div>
</main>'''

html = re.sub(r'<main class="page hidden"\s+id="page-analytics">.*?</main>', new_analytics, html, flags=re.DOTALL)


# 2. Past History Page Replacement
new_history = '''<main class="page hidden pt-24 px-gutter" id="page-history">
    <div class="mb-8">
        <h2 class="text-headline-lg font-bold text-primary-fixed tracking-tight">Patient History</h2>
        <p class="text-body-sm text-on-surface-variant">Archived neurological scan records</p>
    </div>

    <!-- History Stats Row -->
    <div class="grid grid-cols-4 gap-4 mb-8">
        <div class="glass-panel p-4 rounded-xl border-l-4 border-primary">
            <div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Total Scans</div>
            <div class="text-headline-lg font-bold text-on-surface" id="hist-total">0</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border-l-4 border-error">
            <div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Tumors Detected</div>
            <div class="text-headline-lg font-bold text-error" id="hist-tumors">0</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border-l-4 border-green-400">
            <div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">No Tumor Cases</div>
            <div class="text-headline-lg font-bold text-green-400" id="hist-clear">0</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border-l-4 border-secondary">
            <div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Average Confidence</div>
            <div class="text-headline-lg font-bold text-secondary" id="hist-avg-conf">—</div>
        </div>
    </div>

    <!-- History Table Container -->
    <div class="glass-panel p-6 rounded-2xl">
        <div class="flex justify-between items-center mb-6">
            <div class="flex gap-4 items-center">
                <input type="text" id="hist-search" placeholder="Search Patient Name or ID..." class="bg-surface-container border-none rounded-lg px-4 py-2 text-body-sm focus:ring-1 focus:ring-primary w-64">
                <select id="hist-filter" class="bg-surface-container border-none rounded-lg px-4 py-2 text-body-sm focus:ring-1 focus:ring-primary">
                    <option value="all">All Diagnoses</option>
                    <option value="glioma">Glioma</option>
                    <option value="meningioma">Meningioma</option>
                    <option value="pituitary">Pituitary</option>
                    <option value="notumor">No Tumor</option>
                </select>
                <select id="hist-sort" class="bg-surface-container border-none rounded-lg px-4 py-2 text-body-sm focus:ring-1 focus:ring-primary">
                    <option value="newest">Sort by Date (Newest)</option>
                    <option value="oldest">Sort by Date (Oldest)</option>
                </select>
            </div>
            <div class="flex gap-2">
                <button id="export-csv-btn" class="bg-surface-container hover:bg-white/10 text-on-surface px-4 py-2 rounded-lg text-body-sm transition-colors border border-white/10">Export CSV</button>
                <button id="clear-history-btn" class="bg-error/10 hover:bg-error/20 text-error px-4 py-2 rounded-lg text-body-sm transition-colors border border-error/20">Clear All</button>
            </div>
        </div>

        <div class="w-full overflow-x-auto">
            <div class="text-center py-12 text-on-surface-variant hidden" id="history-empty">
                No patient records found. Complete a scan analysis to populate history.
            </div>
            <table class="w-full text-left border-collapse" id="history-table">
                <thead>
                    <tr class="border-b border-white/10 text-on-surface-variant text-[12px] uppercase tracking-wider">
                        <th class="py-3 px-4 font-bold">Patient Name</th>
                        <th class="py-3 px-4 font-bold">Patient ID</th>
                        <th class="py-3 px-4 font-bold">Prediction</th>
                        <th class="py-3 px-4 font-bold">Confidence</th>
                        <th class="py-3 px-4 font-bold">Date</th>
                        <th class="py-3 px-4 font-bold text-right">Actions</th>
                    </tr>
                </thead>
                <tbody id="history-tbody" class="text-body-sm text-on-surface">
                    <!-- Populated by JS -->
                </tbody>
            </table>
        </div>
    </div>
</main>'''

html = re.sub(r'<main class="page hidden"\s+id="page-history">.*?</main>', new_history, html, flags=re.DOTALL)

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
