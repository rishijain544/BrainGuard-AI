import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

monthly_chart_js = '''
        // Render Monthly Scan Trends Chart
        const monthlyCtx = document.getElementById('chart-monthly-trends');
        if (monthlyCtx) {
            if (chartInstances['monthly']) chartInstances['monthly'].destroy();
            
            // Group scans by Month-Year
            const monthlyCounts = {};
            history.forEach(item => {
                const dateObj = new Date(item.patient.scanDate || item.timestamp);
                const monthYear = dateObj.toLocaleString('default', { month: 'short', year: 'numeric' });
                monthlyCounts[monthYear] = (monthlyCounts[monthYear] || 0) + 1;
            });
            
            const labels = Object.keys(monthlyCounts).reverse(); // Oldest to newest if history is sorted newest first
            const data = Object.values(monthlyCounts).reverse();
            
            chartInstances['monthly'] = new Chart(monthlyCtx, {
                type: 'line',
                data: {
                    labels: labels.length ? labels : ['No Data'],
                    datasets: [{
                        label: 'Total Scans',
                        data: data.length ? data : [0],
                        borderColor: '#ff5a36',
                        backgroundColor: 'rgba(255, 90, 54, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#ff5a36',
                        pointRadius: 4,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                        x: { grid: { display: false } }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }
'''

if 'chart-monthly-trends' not in js:
    js = js.replace('// Radar Chart', monthly_chart_js + '\n        // Radar Chart')
    with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
