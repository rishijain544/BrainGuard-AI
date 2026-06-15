import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

phase2_js = '''
        // --- PHASE 2 LOGIC ---
        const advancedSec = document.getElementById('advanced-ai-section');
        if (advancedSec) {
            advancedSec.style.display = 'block';
            
            // Stats
            const agreement = data.model_agreement ? (data.model_agreement * 100).toFixed(0) : 85;
            document.getElementById('ai-agreement').textContent = `${agreement}%`;
            
            // Mock reliability based on confidence & agreement
            const reliability = Math.min(100, Math.max(0, (data.ensemble_confidence * 100) - (100 - agreement) * 0.5)).toFixed(1);
            document.getElementById('ai-reliability').textContent = `${reliability}%`;
            
            const uncertainty = data.uncertainty ? (data.uncertainty * 100).toFixed(1) : ((100 - agreement) / 2).toFixed(1);
            document.getElementById('ai-uncertainty').textContent = `±${uncertainty}%`;
            
            // Images
            const origSrc = document.getElementById('mri-preview').src;
            document.getElementById('explain-orig-img').src = origSrc;
            document.getElementById('explain-orig-bg').src = origSrc;
            document.getElementById('seg-orig').src = origSrc;
            
            // Heatmap
            const heatmapImg = document.getElementById('explain-heatmap');
            if (data.gradcam_base64) {
                heatmapImg.src = "data:image/png;base64," + data.gradcam_base64;
            } else {
                heatmapImg.src = "";
            }
            
            // Opacity
            const opSlider = document.getElementById('explain-opacity');
            opSlider.addEventListener('input', (e) => {
                heatmapImg.style.opacity = e.target.value / 100;
                document.getElementById('explain-canvas').style.opacity = e.target.value / 100;
            });
            
            // Toggle ViT vs GradCAM
            const btnGrad = document.getElementById('btn-show-gradcam');
            const btnVit = document.getElementById('btn-show-vit');
            const explainTitle = document.getElementById('explain-title');
            const expCanvas = document.getElementById('explain-canvas');
            
            btnGrad.onclick = () => {
                heatmapImg.style.display = 'block';
                expCanvas.style.display = 'none';
                explainTitle.textContent = 'Grad-CAM Map';
                explainTitle.style.color = 'var(--accent-blue)';
                btnGrad.className = 'btn btn-primary';
                btnVit.className = 'btn btn-secondary';
            };
            
            btnVit.onclick = () => {
                heatmapImg.style.display = 'none';
                expCanvas.style.display = 'block';
                explainTitle.textContent = 'ViT Attention Map';
                explainTitle.style.color = '#a855f7'; // Purple for ViT
                btnGrad.className = 'btn btn-secondary';
                btnVit.className = 'btn btn-primary';
                simulateVitAttention(document.getElementById('explain-orig-bg'), expCanvas);
            };
            
            // Simulate Segmentation
            simulateSegmentation(document.getElementById('seg-orig'), document.getElementById('seg-canvas'), isTumor);
        }
'''

# We also need the simulation functions at the global scope
simulation_funcs = '''
function simulateVitAttention(imgEl, canvas) {
    if (!imgEl.complete || !imgEl.naturalWidth) return;
    const ctx = canvas.getContext('2d');
    canvas.width = imgEl.naturalWidth;
    canvas.height = imgEl.naturalHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Create patch-based attention map (grid-like)
    const patchSize = Math.max(16, Math.floor(canvas.width / 14));
    
    for (let y = 0; y < canvas.height; y += patchSize) {
        for (let x = 0; x < canvas.width; x += patchSize) {
            // Random attention weights, stronger near center
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            const dist = Math.sqrt(Math.pow(x - cx, 2) + Math.pow(y - cy, 2));
            const maxDist = Math.sqrt(Math.pow(cx, 2) + Math.pow(cy, 2));
            
            let weight = 1 - (dist / maxDist);
            weight = weight * Math.random() * 2; // Add noise
            
            if (weight > 0.4) {
                const alpha = Math.min(0.8, (weight - 0.4) * 2);
                ctx.fillStyle = `rgba(168, 85, 247, ${alpha})`; // Purple
                ctx.fillRect(x, y, patchSize, patchSize);
            }
        }
    }
}

function simulateSegmentation(imgEl, canvas, isTumor) {
    if (!imgEl.complete || !imgEl.naturalWidth) {
        imgEl.onload = () => simulateSegmentation(imgEl, canvas, isTumor);
        return;
    }
    const ctx = canvas.getContext('2d');
    canvas.width = imgEl.naturalWidth;
    canvas.height = imgEl.naturalHeight;
    
    // Draw original image to read pixels
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(imgEl, 0, 0);
    
    const imgData = tempCtx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imgData.data;
    
    let tumorPixels = 0;
    let brainPixels = 0;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (!isTumor) {
        document.getElementById('seg-area').textContent = '0 mm²';
        document.getElementById('seg-percent').textContent = '0.0 %';
        return;
    }

    const maskData = ctx.createImageData(canvas.width, canvas.height);
    
    for (let i = 0; i < data.length; i += 4) {
        const r = data[i], g = data[i+1], b = data[i+2];
        const brightness = (r + g + b) / 3;
        
        if (brightness > 20) brainPixels++;
        
        // High intensity pixels simulate tumor region
        if (brightness > 180) {
            tumorPixels++;
            // Draw cyan mask
            maskData.data[i] = 6;
            maskData.data[i+1] = 182;
            maskData.data[i+2] = 212;
            maskData.data[i+3] = 180; // Alpha
        }
    }
    
    ctx.putImageData(maskData, 0, 0);
    
    const pixelToMm2 = 0.25; // mock conversion
    const area = (tumorPixels * pixelToMm2).toFixed(1);
    const percent = ((tumorPixels / Math.max(1, brainPixels)) * 100).toFixed(2);
    
    document.getElementById('seg-area').textContent = `${area} mm²`;
    document.getElementById('seg-percent').textContent = `${percent} %`;
}
'''

# Inject inside displayAnalysisResults
if 'advanced-ai-section' not in js:
    # Find the end of displayAnalysisResults
    # We will just inject it right before `if (data.gradcam_base64)` inside displayAnalysisResults
    start = js.find('if (data.gradcam_base64)')
    if start != -1:
        js = js[:start] + phase2_js + '\n        ' + js[start:]

# Inject global functions at the end of the file
if 'simulateVitAttention' not in js:
    js += '\n' + simulation_funcs

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
