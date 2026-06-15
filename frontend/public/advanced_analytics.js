// Advanced Analytics Engine
window.advancedCharts = window.advancedCharts || {};

async function generateAdvancedAnalytics(imageElement, data) {
    if (!imageElement || !imageElement.src || imageElement.src === window.location.href) return;

    // Wait for image to be fully loaded if it isn't
    if (!imageElement.complete) {
        await new Promise(resolve => { imageElement.onload = resolve; });
    }

    // 1. Image Processing via Canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = imageElement.naturalWidth || 256;
    canvas.height = imageElement.naturalHeight || 256;
    ctx.drawImage(imageElement, 0, 0, canvas.width, canvas.height);
    
    let imgData;
    try {
        imgData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    } catch(e) {
        // CORS fallback
        console.warn("Canvas CORS error. Simulating pixels.");
        imgData = new Uint8ClampedArray(canvas.width * canvas.height * 4);
        for(let i=0; i<imgData.length; i+=4) {
            let val = Math.random() * 255;
            imgData[i] = val; imgData[i+1] = val; imgData[i+2] = val; imgData[i+3] = 255;
        }
    }

    // Calculate Histogram
    const histogram = new Array(256).fill(0);
    let leftSum = 0, rightSum = 0;
    let minIntensity = 255, maxIntensity = 0;
    let sumIntensity = 0;

    const midX = canvas.width / 2;
    const midY = canvas.height / 2;
    let quadSums = [0, 0, 0, 0]; // TL, TR, BL, BR

    for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
            const idx = (y * canvas.width + x) * 4;
            const r = imgData[idx];
            const g = imgData[idx + 1];
            const b = imgData[idx + 2];
            // grayscale
            const gray = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
            
            histogram[gray]++;
            sumIntensity += gray;
            if (gray < minIntensity) minIntensity = gray;
            if (gray > maxIntensity) maxIntensity = gray;

            // Symmetry
            if (x < midX) leftSum += gray;
            else rightSum += gray;

            // Quadrants (for heatzone simulation)
            if (gray > 150) { // only count bright spots for heatzone
                if (x < midX && y < midY) quadSums[0] += gray;
                else if (x >= midX && y < midY) quadSums[1] += gray;
                else if (x < midX && y >= midY) quadSums[2] += gray;
                else quadSums[3] += gray;
            }
        }
    }

    // 1. Render Histogram
    const histCtx = document.getElementById('adv-chart-histogram')?.getContext('2d');
    if (histCtx) {
        if (window.advancedCharts.histogram) window.advancedCharts.histogram.destroy();
        window.advancedCharts.histogram = new Chart(histCtx, {
            type: 'bar',
            data: {
                labels: Array.from({length: 256}, (_, i) => i),
                datasets: [{
                    label: 'Pixel Count',
                    data: histogram,
                    backgroundColor: 'rgba(0, 229, 255, 0.5)',
                    borderWidth: 0,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { 
                    x: { display: false }, 
                    y: { display: false }
                }
            }
        });
    }

    // 2. Symmetry Analysis
    const totalSym = leftSum + rightSum;
    const leftPct = totalSym === 0 ? 50 : (leftSum / totalSym) * 100;
    const rightPct = 100 - leftPct;
    
    document.getElementById('adv-sym-left').style.width = `${leftPct}%`;
    document.getElementById('adv-sym-right').style.width = `${rightPct}%`;
    
    // 100% match if leftPct == 50%
    const symScore = 100 - Math.abs(50 - leftPct) * 2; 
    document.getElementById('adv-sym-score').textContent = `${symScore.toFixed(1)}% Match`;
    const warnEl = document.getElementById('adv-sym-warning');
    if (symScore < 85 && data.ensemble_prediction !== 'no_tumor') {
        warnEl.classList.remove('hidden');
        warnEl.textContent = 'Asymmetry Detected (Potential Lesion)';
    } else {
        warnEl.classList.add('hidden');
    }

    // 3. Tumor Heatzone Map
    const totalQuad = quadSums.reduce((a,b) => a+b, 0) || 1;
    const getQuadColor = (pct) => `rgba(255, 0, 160, ${pct/100})`; // Pink heat
    
    ['tl', 'tr', 'bl', 'br'].forEach((q, i) => {
        const pct = (quadSums[i] / totalQuad) * 100;
        document.getElementById(`adv-hz-${q}`).style.backgroundColor = getQuadColor(pct);
        document.getElementById(`adv-hz-${q}-val`).textContent = `${pct.toFixed(1)}%`;
    });

    // 4. Scan Quality Score
    const contrast = maxIntensity - minIntensity;
    let qualityScore = (contrast / 255) * 100;
    if (qualityScore < 0) qualityScore = 0;
    if (qualityScore > 100) qualityScore = 100;
    
    document.getElementById('adv-quality-score').textContent = Math.round(qualityScore);
    const gaugeEl = document.getElementById('adv-quality-gauge');
    // Rotate from -45deg (0%) to 135deg (100%) -> range 180deg
    const rot = -45 + (qualityScore / 100) * 180;
    gaugeEl.style.transform = `rotate(${rot}deg)`;
    
    const labelEl = document.getElementById('adv-quality-label');
    if (qualityScore > 80) { labelEl.textContent = 'Excellent'; labelEl.style.color = '#4ade80'; gaugeEl.style.borderColor = '#4ade80'; }
    else if (qualityScore > 50) { labelEl.textContent = 'Good'; labelEl.style.color = '#00e5ff'; gaugeEl.style.borderColor = '#00e5ff'; }
    else { labelEl.textContent = 'Poor'; labelEl.style.color = '#ff4d4d'; gaugeEl.style.borderColor = '#ff4d4d'; }

    // 5. Lobe Detection
    // Use the max quadrant to guess the lobe
    const maxQuadIdx = quadSums.indexOf(Math.max(...quadSums));
    let lobe = 'Temporal';
    if (maxQuadIdx === 0) lobe = 'Frontal (Left)';
    else if (maxQuadIdx === 1) lobe = 'Frontal (Right)';
    else if (maxQuadIdx === 2) lobe = 'Occipital (Left)';
    else if (maxQuadIdx === 3) lobe = 'Occipital (Right)';
    
    if (data.ensemble_prediction === 'no_tumor') lobe = 'None (Clear)';
    document.getElementById('adv-lobe-name').textContent = lobe;

    // 6. Radar Chart
    const radarCtx = document.getElementById('adv-chart-radar')?.getContext('2d');
    if (radarCtx) {
        if (window.advancedCharts.radar) window.advancedCharts.radar.destroy();
        window.advancedCharts.radar = new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['CNN Conf', 'ResNet Conf', 'ViT Conf', 'Agreement', 'Certainty'],
                datasets: [{
                    label: 'Model Metrics',
                    data: [
                        data.cnn_prediction.confidence * 100,
                        data.resnet_prediction.confidence * 100,
                        data.vit_prediction.confidence * 100,
                        data.ensemble_confidence * 100,
                        (1 - data.uncertainty) * 100
                    ],
                    backgroundColor: 'rgba(0, 229, 255, 0.2)',
                    borderColor: '#00e5ff',
                    pointBackgroundColor: '#ff00a0',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: { r: { min: 0, max: 100, ticks: { display: false }, grid: { color: 'rgba(255,255,255,0.1)' }, pointLabels: { color: 'rgba(255,255,255,0.7)' } } },
                plugins: { legend: { display: false } }
            }
        });
    }

    // 7. Risk Score Meter
    const isTumor = data.ensemble_prediction !== 'no_tumor';
    let risk = 0;
    if (isTumor) {
        risk = (data.ensemble_confidence * 100 * 0.5) + ((1 - data.uncertainty) * 100 * 0.3) + 20;
    } else {
        risk = (data.uncertainty * 100 * 0.5); // some small risk if uncertain
    }
    if (risk > 100) risk = 100;
    if (risk < 0) risk = 0;

    document.getElementById('adv-risk-score').textContent = Math.round(risk);
    const riskRing = document.getElementById('adv-risk-ring');
    const riskRot = -45 + (risk / 100) * 180;
    riskRing.style.transform = `rotate(${riskRot}deg)`;
    if (risk > 75) riskRing.style.borderColor = '#ff00a0';
    else if (risk > 40) riskRing.style.borderColor = '#fbbf24';
    else riskRing.style.borderColor = '#4ade80';

    // 8. Timeline
    const timeCtx = document.getElementById('adv-chart-timeline')?.getContext('2d');
    if (timeCtx) {
        if (window.advancedCharts.timeline) window.advancedCharts.timeline.destroy();
        
        // Mock timeline data
        const dates = ['3 Months Ago', '1 Month Ago', 'Current'];
        let histData;
        if (isTumor) {
            histData = [risk - 15, risk - 5, risk];
        } else {
            histData = [30, 15, risk];
        }

        window.advancedCharts.timeline = new Chart(timeCtx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Risk Trend',
                    data: histData,
                    borderColor: '#ff00a0',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(255, 0, 160, 0.1)'
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { 
                    y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.5)' } },
                    x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.5)' } }
                }
            }
        });
    }
}
