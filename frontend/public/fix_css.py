import re

with open('d:/brain_tumour_prediction/frontend/public/landing.css', 'r', encoding='utf-8') as f:
    landing = f.read()

# Make site-header sticky glassmorphism
sticky_header = '''
.site-header {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(18, 18, 20, 0.7) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
'''
landing += sticky_header

with open('d:/brain_tumour_prediction/frontend/public/landing.css', 'w', encoding='utf-8') as f:
    f.write(landing)

with open('d:/brain_tumour_prediction/frontend/public/styles.css', 'r', encoding='utf-8') as f:
    styles = f.read()

# Add responsiveness and clean up spacing
responsive_css = '''
/* Phase 1: Responsive Layout & UI Polish */
@media (max-width: 992px) {
    .app-main-grid {
        grid-template-columns: 1fr !important;
        display: flex !important;
        flex-direction: column !important;
    }
    .grid-column-left {
        grid-template-columns: 1fr !important;
        display: flex !important;
        flex-direction: column !important;
    }
    .stats-row {
        flex-direction: column;
    }
    .charts-row {
        flex-direction: column;
    }
}

.dashboard-card {
    max-width: 100%;
    margin-bottom: 24px;
}

#mri-scan {
    padding-top: 10px !important;
}

.app-container {
    padding: 16px;
}
'''

styles += responsive_css

with open('d:/brain_tumour_prediction/frontend/public/styles.css', 'w', encoding='utf-8') as f:
    f.write(styles)
