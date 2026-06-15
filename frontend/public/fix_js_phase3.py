import os

filepath = 'd:/brain_tumour_prediction/frontend/public/app.js'
with open(filepath, 'a', encoding='utf-8') as f:
    f.write('''

// ==========================================
// PHASE 3: ANALYTICS & PAST HISTORY LOGIC
// ==========================================

// Global Chart Instances
let chartPie, chartBar, chartLine, chartRadar, chartHist, chartMonthly;

function initCharts() {
    Chart.defaults.color = '#a1a1aa';
    Chart.defaults.font.family = 'Inter, sans-serif';
    
    const pieCtx = document.getElementById('chart-pie')?.getContext('2d');
    if (pieCtx && !chartPie) {
        chartPie = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'],
                datasets: [{
                    data: [0,0,0,0],
                    backgroundColor: ['#f59e0b', '#8b5cf6', '#ec4899', '#10b981'],
                    borderWidth: 0
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'right' } } }
        });
    }

    const barCtx = document.getElementById('chart-bar')?.getContext('2d');
    if (barCtx && !chartBar) {
        chartBar = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: ['CNN', 'ResNet50', 'Hybrid ViT'],
                datasets: [{
                    label: 'Avg Confidence',
                    data: [0,0,0],
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#a855f7'],
                    borderRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
        });
    }
    
    const lineCtx = document.getElementById('chart-line')?.getContext('2d');
    if (lineCtx && !chartLine) {
        chartLine = new Chart(lineCtx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Ensemble Confidence', data: [], borderColor: '#06b6d4', tension: 0.4, fill: true, backgroundColor: 'rgba(6, 182, 212, 0.1)' }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
        });
    }

    const radarCtx = document.getElementById('chart-radar')?.getContext('2d');
    if (radarCtx && !chartRadar) {
        chartRadar = new Chart(radarCtx, {
            type: 'radar',
            data: { labels: ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'], datasets: [{ label: 'Detection Frequency', data: [0,0,0,0], backgroundColor: 'rgba(59, 130, 246, 0.2)', borderColor: '#3b82f6', pointBackgroundColor: '#3b82f6' }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { r: { ticks: { display: false }, grid: { color: 'rgba(255,255,255,0.1)' }, angleLines: { color: 'rgba(255,255,255,0.1)' } } } }
        });
    }

    const histCtx = document.getElementById('chart-hist')?.getContext('2d');
    if (histCtx && !chartHist) {
        chartHist = new Chart(histCtx, {
            type: 'bar',
            data: { labels: ['0-20%','20-40%','40-60%','60-80%','80-100%'], datasets: [{ label: 'Number of Scans', data: [0,0,0,0,0], backgroundColor: '#10b981' }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
        });
    }
    
    const monthlyCtx = document.getElementById('chart-monthly-trends')?.getContext('2d');
    if (monthlyCtx && !chartMonthly) {
        chartMonthly = new Chart(monthlyCtx, {
            type: 'bar',
            data: { labels: [], datasets: [{ label: 'Scans', data: [], backgroundColor: '#6366f1', borderRadius: 4 }] },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}

function updateAnalyticsPage() {
    initCharts();
    
    const scans = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    const total = scans.length;
    
    if (total === 0) {
        document.getElementById('ana-total-scans').textContent = '0';
        document.getElementById('ana-avg-conf').textContent = '—';
        document.getElementById('ana-best-model').textContent = '—';
        document.getElementById('ana-tumor-rate').textContent = '—';
        
        ['pie','bar','line','radar','hist'].forEach(id => {
            const chartCanvas = document.getElementById('chart-' + id);
            const noData = document.getElementById('ana-no-data-' + id);
            if (chartCanvas) chartCanvas.classList.add('hidden');
            if (noData) noData.style.display = 'flex';
        });
        return;
    }
    
    ['pie','bar','line','radar','hist'].forEach(id => {
        const chartCanvas = document.getElementById('chart-' + id);
        const noData = document.getElementById('ana-no-data-' + id);
        if (chartCanvas) chartCanvas.classList.remove('hidden');
        if (noData) noData.style.display = 'none';
    });

    let tumors = 0;
    let sumConf = 0;
    let counts = { glioma: 0, meningioma: 0, pituitary: 0, notumor: 0 };
    let cnnSum=0, resSum=0, vitSum=0;
    let confHistory = [];
    let histBins = [0,0,0,0,0];
    
    scans.forEach((s, idx) => {
        const isTumor = s.ensemble_prediction !== 'notumor';
        if (isTumor) tumors++;
        
        sumConf += s.ensemble_confidence;
        
        if (counts[s.ensemble_prediction] !== undefined) {
            counts[s.ensemble_prediction]++;
        }
        
        cnnSum += s.models.cnn.confidence;
        resSum += s.models.resnet.confidence;
        vitSum += s.models.vit.confidence;
        
        confHistory.push((s.ensemble_confidence * 100).toFixed(1));
        
        const cVal = s.ensemble_confidence;
        if (cVal <= 0.2) histBins[0]++;
        else if (cVal <= 0.4) histBins[1]++;
        else if (cVal <= 0.6) histBins[2]++;
        else if (cVal <= 0.8) histBins[3]++;
        else histBins[4]++;
    });
    
    document.getElementById('ana-total-scans').textContent = total;
    document.getElementById('ana-avg-conf').textContent = ((sumConf / total) * 100).toFixed(1) + '%';
    document.getElementById('ana-best-model').textContent = 'Hybrid ViT';
    document.getElementById('ana-tumor-rate').textContent = ((tumors / total) * 100).toFixed(1) + '%';
    
    if (chartPie) { chartPie.data.datasets[0].data = [counts.glioma, counts.meningioma, counts.pituitary, counts.notumor]; chartPie.update(); }
    if (chartBar) { chartBar.data.datasets[0].data = [(cnnSum/total)*100, (resSum/total)*100, (vitSum/total)*100]; chartBar.update(); }
    if (chartLine) { 
        chartLine.data.labels = scans.map((_, i) => 'Scan ' + (i+1));
        chartLine.data.datasets[0].data = confHistory;
        chartLine.update();
    }
    if (chartRadar) { chartRadar.data.datasets[0].data = [counts.glioma, counts.meningioma, counts.pituitary, counts.notumor]; chartRadar.update(); }
    if (chartHist) { chartHist.data.datasets[0].data = histBins; chartHist.update(); }
    
    if (chartMonthly) {
        chartMonthly.data.labels = [new Date().toLocaleDateString('default', { month: 'short' })];
        chartMonthly.data.datasets[0].data = [total];
        chartMonthly.update();
    }
}

function updateHistoryPage() {
    const scans = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    
    const tbody = document.getElementById('history-tbody');
    const emptyState = document.getElementById('history-empty');
    const tableWrapper = document.querySelector('.table-wrapper');
    
    let tumors = 0;
    let sumConf = 0;
    
    scans.forEach(s => {
        if (s.ensemble_prediction !== 'notumor') tumors++;
        sumConf += s.ensemble_confidence;
    });
    
    document.getElementById('hist-total').textContent = scans.length;
    document.getElementById('hist-tumors').textContent = tumors;
    document.getElementById('hist-clear').textContent = scans.length - tumors;
    document.getElementById('hist-avg-conf').textContent = scans.length > 0 ? ((sumConf / scans.length) * 100).toFixed(1) + '%' : '—';
    
    if (scans.length === 0) {
        if (emptyState) emptyState.classList.remove('hidden');
        if (tableWrapper) tableWrapper.style.display = 'none';
        if (tbody) tbody.innerHTML = '';
        return;
    }
    
    if (emptyState) emptyState.classList.add('hidden');
    if (tableWrapper) tableWrapper.style.display = 'block';
    
    renderHistoryTable(scans);
}

function renderHistoryTable(scans) {
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;
    
    const searchTerm = (document.getElementById('hist-search')?.value || '').toLowerCase();
    const filterType = document.getElementById('hist-filter')?.value || 'all';
    
    tbody.innerHTML = '';
    
    scans.forEach((s, idx) => {
        const pName = (s.patientName || 'Unknown').toLowerCase();
        const pId = (s.patientId || '').toLowerCase();
        const pDiag = s.ensemble_prediction.toLowerCase();
        
        if (searchTerm && !pName.includes(searchTerm) && !pId.includes(searchTerm)) return;
        if (filterType !== 'all' && pDiag !== filterType) return;
        
        const isTumor = s.ensemble_prediction !== 'notumor';
        const badgeClass = `badge-${pDiag}`;
        const diagLabel = pDiag.charAt(0).toUpperCase() + pDiag.slice(1);
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${idx + 1}</td>
            <td><strong>${s.patientName || 'N/A'}</strong></td>
            <td>${s.patientId || 'N/A'}</td>
            <td>${s.patientAge || 'N/A'}</td>
            <td>${new Date(s.timestamp).toLocaleDateString()}</td>
            <td><span class="${badgeClass}">${diagLabel}</span></td>
            <td><strong>${(s.ensemble_confidence * 100).toFixed(1)}%</strong></td>
            <td style="color: #3b82f6;">${(s.models.cnn.confidence * 100).toFixed(1)}%</td>
            <td style="color: #8b5cf6;">${(s.models.resnet.confidence * 100).toFixed(1)}%</td>
            <td style="color: #a855f7;">${(s.models.vit.confidence * 100).toFixed(1)}%</td>
            <td>
                <button class="btn-delete-row" data-idx="${idx}">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    // Add delete listeners
    document.querySelectorAll('.btn-delete-row').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.getAttribute('data-idx'));
            const allScans = JSON.parse(localStorage.getItem('scanHistory') || '[]');
            allScans.splice(index, 1);
            localStorage.setItem('scanHistory', JSON.stringify(allScans));
            updateAnalyticsPage();
            updateHistoryPage();
        });
    });
}

// Ensure the code runs when navigating to Analytics or History
document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
        const page = e.target.getAttribute('data-page');
        if (page === 'analytics') {
            setTimeout(updateAnalyticsPage, 100);
        } else if (page === 'history') {
            setTimeout(updateHistoryPage, 100);
        }
    });
});

// History Inputs
document.getElementById('hist-search')?.addEventListener('input', () => {
    renderHistoryTable(JSON.parse(localStorage.getItem('scanHistory') || '[]'));
});
document.getElementById('hist-filter')?.addEventListener('change', () => {
    renderHistoryTable(JSON.parse(localStorage.getItem('scanHistory') || '[]'));
});
document.getElementById('clear-history-btn')?.addEventListener('click', () => {
    if(confirm('Are you sure you want to clear all history?')) {
        localStorage.removeItem('scanHistory');
        updateAnalyticsPage();
        updateHistoryPage();
    }
});
document.getElementById('export-csv-btn')?.addEventListener('click', () => {
    const scans = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    if (scans.length === 0) return alert('No data to export');
    
    let csv = "Patient Name,Patient ID,Age,Date,Diagnosis,Confidence,CNN,ResNet,ViT\\n";
    scans.forEach(s => {
        csv += `${s.patientName || ''},${s.patientId || ''},${s.patientAge || ''},${new Date(s.timestamp).toLocaleDateString()},${s.ensemble_prediction},${(s.ensemble_confidence*100).toFixed(1)},${(s.models.cnn.confidence*100).toFixed(1)},${(s.models.resnet.confidence*100).toFixed(1)},${(s.models.vit.confidence*100).toFixed(1)}\\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'BrainGuard_Scan_History.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// Run once on load just in case
setTimeout(() => {
    updateAnalyticsPage();
    updateHistoryPage();
}, 500);

''')
