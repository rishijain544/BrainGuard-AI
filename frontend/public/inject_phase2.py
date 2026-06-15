import re
with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

phase2_html = '''
        <!-- ============================================== -->
        <!-- PHASE 2: ADVANCED AI VISUALIZATIONS -->
        <!-- ============================================== -->
        <div id="advanced-ai-section" style="display: none; margin-top: 32px; animation: dashboardReveal 0.6s ease-out forwards;">
            <div class="stats-row" style="margin-bottom: 24px;">
                <!-- Ensemble Intelligence -->
                <div class="dashboard-card stat-card" style="flex:1;">
                    <div class="stat-icon"><svg viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg></div>
                    <div class="stat-content">
                        <h3>Model Agreement</h3>
                        <div class="stat-value" id="ai-agreement">--%</div>
                    </div>
                </div>
                <div class="dashboard-card stat-card" style="flex:1;">
                    <div class="stat-icon"><svg viewBox="0 0 24 24" fill="none"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2"/></svg></div>
                    <div class="stat-content">
                        <h3>Reliability Score</h3>
                        <div class="stat-value" id="ai-reliability">--%</div>
                    </div>
                </div>
                <div class="dashboard-card stat-card" style="flex:1;">
                    <div class="stat-icon"><svg viewBox="0 0 24 24" fill="none"><path d="M13 10V3L4 14h7v8l9-11h-7z" stroke="currentColor" stroke-width="2"/></svg></div>
                    <div class="stat-content">
                        <h3>Prediction Uncertainty</h3>
                        <div class="stat-value" id="ai-uncertainty">±--%</div>
                    </div>
                </div>
            </div>

            <div class="charts-row" style="display: flex; gap: 24px;">
                <!-- Explainability Center -->
                <div class="dashboard-card" style="flex: 1.5;">
                    <div class="card-header">
                        <h2>Advanced Explainability</h2>
                        <p>Side-by-side comparative analysis of model attention</p>
                    </div>
                    <div class="card-body">
                        <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                            <button class="btn btn-primary" id="btn-show-gradcam" style="flex:1;">Grad-CAM (CNN)</button>
                            <button class="btn btn-secondary" id="btn-show-vit" style="flex:1;">ViT Attention</button>
                        </div>
                        <div style="display: flex; gap: 16px;">
                            <div style="flex: 1; text-align: center;">
                                <h4 style="margin-bottom: 8px; color: var(--text-secondary);">Original MRI</h4>
                                <img id="explain-orig-img" src="" style="width: 100%; border-radius: 8px; border: 1px solid var(--border-color);">
                            </div>
                            <div style="flex: 1; text-align: center;">
                                <h4 style="margin-bottom: 8px; color: var(--accent-blue);" id="explain-title">Grad-CAM Map</h4>
                                <div style="position: relative; width: 100%;">
                                    <img id="explain-orig-bg" src="" style="width: 100%; border-radius: 8px;">
                                    <img id="explain-heatmap" src="" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.6; mix-blend-mode: overlay; border-radius: 8px;">
                                    <canvas id="explain-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none; opacity: 0.7; border-radius: 8px;"></canvas>
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 16px;">
                            <label>Heatmap Opacity</label>
                            <input type="range" id="explain-opacity" min="0" max="100" value="60" style="width: 100%;">
                        </div>
                    </div>
                </div>

                <!-- Segmentation Center -->
                <div class="dashboard-card" style="flex: 1;">
                    <div class="card-header">
                        <h2>Segmentation Center</h2>
                        <p>Attention U-Net tumor boundaries</p>
                    </div>
                    <div class="card-body" style="text-align: center;">
                        <div style="position: relative; width: 100%; max-width: 300px; margin: 0 auto 24px auto;">
                            <img id="seg-orig" src="" style="width: 100%; border-radius: 8px;">
                            <canvas id="seg-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 8px; opacity: 0.5; mix-blend-mode: screen;"></canvas>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.2); padding: 16px; border-radius: 8px; border: 1px solid var(--border-color);">
                            <div>
                                <div style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Tumor Area</div>
                                <div style="font-size: 20px; font-weight: bold; color: var(--accent-blue);" id="seg-area">-- mm²</div>
                            </div>
                            <div>
                                <div style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Brain Mass %</div>
                                <div style="font-size: 20px; font-weight: bold; color: #f59e0b;" id="seg-percent">-- %</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
'''

if 'id="advanced-ai-section"' not in html:
    # Insert after the end of #results-container content but before <!-- End results-container -->
    start = html.find('<!-- End results-container -->')
    if start != -1:
        html = html[:start] + phase2_html + html[start:]
        with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
            f.write(html)
