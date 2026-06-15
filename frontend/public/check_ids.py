with open('d:/brain_tumour_prediction/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

ids_to_check = [
    'dropzone', 'file-input', 'preview-container', 'image-preview', 'remove-img-btn',
    'analyze-btn', 'status-badge', 'device-info', 'results-placeholder', 'results-container',
    'diag-badge', 'gauge-fill', 'gauge-value', 'stat-agreement', 'stat-agreement-bar',
    'stat-uncertainty', 'stat-uncertainty-bar', 'stat-ci', 'view-original', 'view-overlay',
    'opacity-slider', 'opacity-pct', 'model-cnn-pred', 'model-cnn-conf', 'model-resnet-pred',
    'model-resnet-conf', 'model-vit-pred', 'model-vit-conf', 'rec-box', 'rec-title',
    'rec-action', 'download-pdf-btn', 'patient-name', 'patient-id', 'patient-age',
    'scan-date', 'settings-btn', 'settings-modal', 'close-modal-btn', 'api-url-input',
    'modal-test-status', 'save-settings-btn', 'btn-gradcam', 'btn-segmentation',
    'view-segmentation'
]

missing = [i for i in ids_to_check if f'id="{i}"' not in html]
print("Missing IDs:", missing)
