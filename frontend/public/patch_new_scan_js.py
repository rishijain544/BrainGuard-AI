with open('d:/brain_tumour_prediction/frontend/public/app.js', 'a', encoding='utf-8') as f:
    f.write('''
// ────────────────────────────────────────────────────────
// NEW SCAN RESET LOGIC
// ────────────────────────────────────────────────────────
document.getElementById('new-scan-btn')?.addEventListener('click', () => {
    // 1. Clear patient inputs
    document.getElementById('patient-name').value = '';
    document.getElementById('patient-id').value = '';
    document.getElementById('patient-age').value = '';
    document.getElementById('scan-date').value = '';
    
    // 2. Clear case ID
    const caseEl = document.getElementById('ui-case-id');
    if (caseEl) caseEl.textContent = 'Case #Pending';
    
    // 3. Clear prediction cache
    window.currentPrediction = null;
    
    // 4. Reset UI metrics
    const elementsToReset = [
        { id: 'ui-diagnosis-subtitle', default: 'Awaiting scan data...' },
        { id: 'gauge-value', default: '0.0' },
        { id: 'ui-tumor-volume', default: '-- cm³' },
        { id: 'ui-overall-risk', default: '--' },
        { id: 'ui-cnn-conf', default: '--%' },
        { id: 'ui-cnn-pred', default: 'Pending' },
        { id: 'ui-resnet-conf', default: '--%' },
        { id: 'ui-resnet-pred', default: 'Pending' },
        { id: 'ui-vit-conf', default: '--%' },
        { id: 'ui-vit-pred', default: 'Pending' },
        { id: 'ui-location', default: '--' },
        { id: 'ui-contrast', default: '--' },
        { id: 'ui-edema', default: '--' },
        { id: 'ui-vascular', default: '--' }
    ];
    
    elementsToReset.forEach(item => {
        const el = document.getElementById(item.id);
        if (el) el.textContent = item.default;
    });

    // 5. Reset image preview
    const imgEl = document.getElementById('image-preview');
    if (imgEl) imgEl.src = '#'; // or clear it

    const dropzone = document.getElementById('dropzone');
    if (dropzone) {
        dropzone.style.display = 'flex'; // show the dropzone
    }
    
    // 6. Switch to dashboard
    window.switchPage('dashboard');
});
''')
