import re
with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

monthly_chart = '''
                <div class="dashboard-card chart-card chart-card-wide" style="width: 100%;">
                    <div class="card-header"><h2>Monthly Scan Trends</h2><p>Number of scans processed over time</p></div>
                    <div class="card-body chart-body" style="height: 300px;">
                        <canvas id="chart-monthly-trends"></canvas>
                    </div>
                </div>
'''

if 'chart-monthly-trends' not in html:
    # Append to the charts row in the global aggregates section
    start_global = html.find('<h2>Global Historical Aggregates</h2>')
    if start_global == -1: start_global = html.find('Global Historical Aggregates')
    if start_global != -1:
        # Just put it right before the closing div of page-analytics
        end_main = html.find('</main>', start_global)
        html = html[:end_main] + monthly_chart + html[end_main:]
        
        with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
            f.write(html)
