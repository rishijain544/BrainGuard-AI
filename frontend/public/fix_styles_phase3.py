with open('d:/brain_tumour_prediction/frontend/public/styles.css', 'a', encoding='utf-8') as f:
    f.write('''

/* =========================================
   PHASE 3: Analytics & History CSS Fixes
   ========================================= */

/* Fix Oversized SVGs in Stat Cards */
.stat-card-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    margin-right: 16px;
    flex-shrink: 0;
}
.stat-card-icon svg {
    width: 24px !important;
    height: 24px !important;
}

/* History Empty State SVG fix */
.history-empty svg {
    width: 64px !important;
    height: 64px !important;
    margin-bottom: 16px;
}

/* History Table Styling */
.history-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
    font-size: 14px;
}
.history-table th, .history-table td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}
.history-table th {
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    font-size: 12px;
}
.history-table tr:hover {
    background: rgba(255, 255, 255, 0.02);
}

/* Delete Button in Table */
.btn-delete-row {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;
}
.btn-delete-row:hover {
    background: #ef4444;
    color: white;
}

/* Color codes for Table Badges */
.badge-glioma { color: #f59e0b; background: rgba(245, 158, 11, 0.1); padding: 4px 8px; border-radius: 4px; }
.badge-meningioma { color: #8b5cf6; background: rgba(139, 92, 246, 0.1); padding: 4px 8px; border-radius: 4px; }
.badge-pituitary { color: #ec4899; background: rgba(236, 72, 153, 0.1); padding: 4px 8px; border-radius: 4px; }
.badge-notumor { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 4px 8px; border-radius: 4px; }

/* Chart No Data Empty State */
.chart-no-data {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
    color: var(--text-secondary);
    font-style: italic;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    border: 1px dashed var(--border-color);
    position: absolute;
    top: 0; left: 0;
}
.chart-body {
    position: relative;
}
''')
