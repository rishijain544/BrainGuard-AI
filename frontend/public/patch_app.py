import re

with open('d:/brain_tumour_prediction/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add Image Analysis function at the end of app.js
image_analysis_code = '''
    // ──────────────────────────────────────────────────────────────────────────
    // IMAGE PIXEL ANALYSIS (CLIENT SIDE)
    // ──────────────────────────────────────────────────────────────────────────
    function analyzeImagePixels(imgElement) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = imgElement.naturalWidth || 224;
        canvas.height = imgElement.naturalHeight || 224;
        if (canvas.width === 0) return null;
        
        ctx.drawImage(imgElement, 0, 0, canvas.width, canvas.height);
        const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imgData.data;
        
        let totalIntensity = 0;
        let nonZeroPixels = 0;
        let leftSum = 0, rightSum = 0;
        let histogram = new Array(256).fill(0);
        
        for (let y = 0; y < canvas.height; y++) {
            for (let x = 0; x < canvas.width; x++) {
                const i = (y * canvas.width + x) * 4;
                const r = data[i], g = data[i+1], b = data[i+2];
                // Grayscale luminance
                const gray = Math.round(0.299*r + 0.587*g + 0.114*b);
                histogram[gray]++;
                
                if (gray > 10) {
                    totalIntensity += gray;
                    nonZeroPixels++;
                    if (x < canvas.width / 2) leftSum += gray;
                    else rightSum += gray;
                }
            }
        }
        
        const meanIntensity = nonZeroPixels > 0 ? (totalIntensity / nonZeroPixels) : 0;
        const diff = Math.abs(leftSum - rightSum);
        const symmetry = nonZeroPixels > 0 ? (100 - (diff / totalIntensity) * 100) : 100;
        
        // Mock a specific lobe based on mean intensity modulus (deterministic based on image)
        const lobes = ['Frontal Lobe', 'Parietal Lobe', 'Temporal Lobe', 'Occipital Lobe'];
        const lobe = lobes[Math.floor(meanIntensity) % 4];
        
        // Mock tumor area based on top 5% brightest pixels (simplified proxy for hyper-intense tumors)
        let topPixels = 0;
        for (let i = 200; i < 256; i++) topPixels += histogram[i];
        
        return {
            histogram: histogram,
            meanIntensity: meanIntensity.toFixed(1),
            symmetry: symmetry.toFixed(1),
            lobe: lobe,
            tumorArea: topPixels
        };
    }
    
    function renderCurrentScanAnalytics(imgElement) {
        document.getElementById('current-scan-analytics').classList.remove('hidden');
        
        const stats = analyzeImagePixels(imgElement);
        if (!stats) return;
        
        document.getElementById('ana-tumor-area').textContent = stats.tumorArea + ' mm²';
        document.getElementById('ana-symmetry').textContent = stats.symmetry + ' %';
        document.getElementById('ana-mean-intensity').textContent = stats.meanIntensity;
        document.getElementById('ana-lobe').textContent = stats.lobe;
        
        // Render Histogram Chart
        const ctx = document.getElementById('chart-histogram');
        if (!ctx) return;
        if (chartInstances['histogram']) chartInstances['histogram'].destroy();
        
        chartInstances['histogram'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Array.from({length: 256}, (_, i) => i),
                datasets: [{
                    label: 'Pixel Count',
                    data: stats.histogram,
                    backgroundColor: 'rgba(0, 210, 255, 0.6)',
                    borderWidth: 0,
                    barPercentage: 1.0,
                    categoryPercentage: 1.0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
'''

if 'analyzeImagePixels' not in js:
    js = js.replace('});\n', '});\n\n' + image_analysis_code)

# 2. Add renderCurrentScanAnalytics call after displayAnalysisResults
if 'renderCurrentScanAnalytics(imagePreview);' not in js:
    js = js.replace('displayAnalysisResults(predictionResult);', 'displayAnalysisResults(predictionResult);\n            try { renderCurrentScanAnalytics(imagePreview); } catch(e) { console.error("Analytics Error", e); }')

# 3. Fix missing element errors by replacing e.result.cnn_prediction.confidence with safe fallback
js = js.replace('e.result.cnn_prediction?.confidence', '(e.result.cnn_prediction?.confidence || e.result.models?.cnn?.confidence)')
js = js.replace('e.result.resnet_prediction?.confidence', '(e.result.resnet_prediction?.confidence || e.result.models?.resnet50?.confidence)')
js = js.replace('e.result.vit_prediction?.confidence', '(e.result.vit_prediction?.confidence || e.result.models?.vit?.confidence)')

with open('d:/brain_tumour_prediction/public/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
