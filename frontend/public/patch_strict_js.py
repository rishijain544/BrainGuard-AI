import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Update `renderHistory` to support sorting and the 5-column table
new_render_history = '''function renderHistory() {
        const history = loadHistory();
        const tbody = document.getElementById('history-tbody');
        const emptyEl = document.getElementById('history-empty');
        const tableEl = document.getElementById('history-table');
        const searchInput = document.getElementById('hist-search');
        const filterSelect = document.getElementById('hist-filter');
        const sortSelect = document.getElementById('hist-sort');

        if (!tbody || !emptyEl || !tableEl) return;

        document.getElementById('hist-total').textContent = history.length;
        document.getElementById('hist-tumors').textContent = history.filter(h => h.result.ensemble_prediction !== 'notumor').length;
        document.getElementById('hist-clear').textContent = history.filter(h => h.result.ensemble_prediction === 'notumor').length;
        document.getElementById('hist-avg-conf').textContent = history.length ? (history.reduce((a,b)=>a+b.result.ensemble_confidence,0)/history.length*100).toFixed(1)+'%' : '—';

        const search = (searchInput?.value || '').toLowerCase();
        const filter = filterSelect?.value || 'all';
        const sortOrder = sortSelect?.value || 'newest';

        let filtered = history.filter(entry => {
            const matchSearch = !search || 
                entry.patient.name.toLowerCase().includes(search) || 
                entry.patient.id.toLowerCase().includes(search);
            const matchFilter = filter === 'all' || entry.result.ensemble_prediction === filter;
            return matchSearch && matchFilter;
        });

        filtered.sort((a, b) => {
            const timeA = new Date(a.patient.scanDate).getTime() || a.id;
            const timeB = new Date(b.patient.scanDate).getTime() || b.id;
            return sortOrder === 'newest' ? timeB - timeA : timeA - timeB;
        });

        tbody.innerHTML = '';
        if (filtered.length === 0) {
            emptyEl.classList.remove('hidden');
            tableEl.classList.add('hidden');
        } else {
            emptyEl.classList.add('hidden');
            tableEl.classList.remove('hidden');

            filtered.forEach((entry) => {
                const r = entry.result;
                const p = entry.patient;
                const isTumor = r.ensemble_prediction !== 'notumor';
                const confPct = (r.ensemble_confidence * 100).toFixed(1);

                const row = document.createElement('tr');
                row.className = 'border-b border-white/5 hover:bg-white/5 transition-colors';
                row.innerHTML = `
                    <td class="py-3 px-4 font-bold text-on-surface">${p.name}</td>
                    <td class="py-3 px-4 text-on-surface-variant font-mono-data">${p.id}</td>
                    <td class="py-3 px-4">
                        <span class="px-2 py-1 rounded text-[10px] font-bold tracking-widest uppercase ${isTumor ? 'bg-error/20 text-error' : 'bg-primary/20 text-primary-fixed'}">
                            ${getDisplayName(r.ensemble_prediction)}
                        </span>
                    </td>
                    <td class="py-3 px-4">${confPct}%</td>
                    <td class="py-3 px-4 text-on-surface-variant">${p.scanDate}</td>
                    <td class="py-3 px-4 text-right">
                        <button class="text-error hover:text-error/80 px-2 transition-colors" onclick="deleteHistoryItem(${entry.id})">Delete</button>
                    </td>`;
                tbody.appendChild(row);
            });
        }
    }

    document.getElementById('hist-search')?.addEventListener('input', renderHistory);
    document.getElementById('hist-filter')?.addEventListener('change', renderHistory);
    document.getElementById('hist-sort')?.addEventListener('change', renderHistory);
'''
js = re.sub(r'function renderHistory\(\) \{.*?(?=window\.deleteHistoryItem)', new_render_history, js, flags=re.DOTALL)


# Update `renderAnalytics` to support Recent Predictions and the updated charts/stats
new_render_analytics = '''function renderAnalytics() {
        const history = loadHistory();
        if (!document.getElementById('chart-pie')) return;

        // Stats
        document.getElementById('ana-total-scans').textContent = history.length;
        if (history.length > 0) {
            const tumors = history.filter(e => e.result.ensemble_prediction !== 'notumor').length;
            const clear = history.filter(e => e.result.ensemble_prediction === 'notumor').length;
            const avgConf = history.reduce((s, e) => s + e.result.ensemble_confidence, 0) / history.length;
            
            document.getElementById('ana-tumor-count').textContent = tumors;
            document.getElementById('ana-clear-count').textContent = clear;
            document.getElementById('ana-avg-conf').textContent = `${(avgConf * 100).toFixed(1)}%`;
        } else {
            document.getElementById('ana-tumor-count').textContent = '0';
            document.getElementById('ana-clear-count').textContent = '0';
            document.getElementById('ana-avg-conf').textContent = '—';
        }

        const shows = history.length > 0;
        ['pie','line','bar','trend'].forEach(id => {
            const noData = document.getElementById(`ana-no-data-${id}`);
            const canvas = document.getElementById(`chart-${id}`);
            if (noData && canvas) {
                if (shows) { noData.classList.add('hidden'); canvas.classList.remove('hidden'); }
                else { noData.classList.remove('hidden'); canvas.classList.add('hidden'); }
            }
        });

        // Recent Predictions Table
        const recentTbody = document.getElementById('ana-recent-tbody');
        const recentEmpty = document.getElementById('ana-recent-empty');
        const recentTable = document.getElementById('ana-recent-table');
        
        if (recentTbody && recentEmpty && recentTable) {
            recentTbody.innerHTML = '';
            if (history.length === 0) {
                recentEmpty.classList.remove('hidden');
                recentTable.classList.add('hidden');
            } else {
                recentEmpty.classList.add('hidden');
                recentTable.classList.remove('hidden');
                const recent = history.slice(0, 5); // top 5
                recent.forEach(entry => {
                    const r = entry.result;
                    const isTumor = r.ensemble_prediction !== 'notumor';
                    const row = document.createElement('tr');
                    row.className = 'border-b border-white/5 hover:bg-white/5 transition-colors';
                    row.innerHTML = `
                        <td class="py-2 px-4">${entry.patient.name}</td>
                        <td class="py-2 px-4 text-[10px] font-bold uppercase tracking-widest ${isTumor ? 'text-error' : 'text-primary'}">${getDisplayName(r.ensemble_prediction)}</td>
                        <td class="py-2 px-4">${(r.ensemble_confidence * 100).toFixed(1)}%</td>
                        <td class="py-2 px-4 text-on-surface-variant">${entry.patient.scanDate}</td>
                    `;
                    recentTbody.appendChild(row);
                });
            }
        }

        if (!shows) return;

        // Destroy old
        Object.values(chartInstances).forEach(c => c.destroy());
        chartInstances = {};

        Chart.defaults.color = '#bac9cc';
        Chart.defaults.font.family = "'Inter', sans-serif";

        // Pie Chart
        const counts = { glioma: 0, meningioma: 0, pituitary: 0, notumor: 0 };
        history.forEach(h => counts[h.result.ensemble_prediction]++);
        chartInstances['pie'] = new Chart(document.getElementById('chart-pie'), {
            type: 'doughnut',
            data: { labels: ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'], datasets: [{ data: [counts.glioma, counts.meningioma, counts.pituitary, counts.notumor], backgroundColor: ['#ffb4ab', '#d1bcff', '#9cf0ff', '#849396'], borderWidth: 0 }] },
            options: { maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });

        // Scan Activity (Line) - Mocks monthly activity based on history counts
        chartInstances['line'] = new Chart(document.getElementById('chart-line'), {
            type: 'line',
            data: { labels: ['Jan','Feb','Mar','Apr','May','Jun'], datasets: [{ label: 'Scans', data: [0, 0, 0, 0, 0, history.length], borderColor: '#00daf3', tension: 0.4 }] },
            options: { maintainAspectRatio: false }
        });

        // Model Performance Bar Chart
        let sums = { cnn: 0, resnet: 0, vit: 0, count: 0 };
        history.forEach(h => {
            sums.cnn += h.result.cnn_prediction?.confidence || h.result.models?.cnn?.confidence || 0;
            sums.resnet += h.result.resnet_prediction?.confidence || h.result.models?.resnet?.confidence || 0;
            sums.vit += h.result.vit_prediction?.confidence || h.result.models?.vit?.confidence || 0;
            sums.count++;
        });
        chartInstances['bar'] = new Chart(document.getElementById('chart-bar'), {
            type: 'bar',
            data: { labels: ['CNN', 'ResNet50', 'Hybrid ViT'], datasets: [{ label: 'Avg Confidence', data: [sums.cnn/sums.count*100, sums.resnet/sums.count*100, sums.vit/sums.count*100], backgroundColor: ['#00daf3', '#7000ff', '#ffb4ab'] }] },
            options: { maintainAspectRatio: false }
        });
        
        // Confidence Trend Chart
        chartInstances['trend'] = new Chart(document.getElementById('chart-trend'), {
            type: 'line',
            data: { labels: history.slice(0,10).map((_, i) => `Scan ${i+1}`), datasets: [{ label: 'Ensemble Confidence', data: history.slice(0,10).map(h => h.result.ensemble_confidence * 100).reverse(), borderColor: '#ffb4ab', tension: 0.4 }] },
            options: { maintainAspectRatio: false }
        });
    }
'''
js = re.sub(r'function renderAnalytics\(\) \{.*?\}\n\}\);\s*$', new_render_analytics + '\n});\n', js, flags=re.DOTALL)

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
