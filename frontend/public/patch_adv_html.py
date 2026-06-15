import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_analytics_html = """
    <!-- Current Scan Advanced Analytics -->
    <div class="mb-4 mt-8 flex justify-between items-center">
        <h3 class="font-bold text-on-surface text-title-md">Current Scan Advanced Analytics</h3>
        <span class="text-[12px] font-mono-data text-primary px-3 py-1 bg-primary/10 rounded-full border border-primary/20" id="adv-scan-id">No Scan Active</span>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-8">
        <!-- 1. Pixel Intensity Histogram -->
        <div class="glass-panel p-6 rounded-2xl lg:col-span-2">
            <h4 class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">1. Pixel Intensity Histogram</h4>
            <div class="relative h-48 w-full flex items-center justify-center">
                <canvas id="adv-chart-histogram"></canvas>
            </div>
            <p class="text-[10px] text-on-surface-variant mt-2 text-center">Grayscale distribution (Dark vs Bright regions)</p>
        </div>

        <!-- 2. Brain Symmetry Analysis -->
        <div class="glass-panel p-6 rounded-2xl">
            <h4 class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">2. Brain Symmetry</h4>
            <div class="flex flex-col items-center justify-center h-48 gap-4">
                <div class="w-full flex justify-between text-[10px] font-bold text-on-surface">
                    <span>Left Hemisphere</span>
                    <span>Right Hemisphere</span>
                </div>
                <div class="w-full h-4 bg-surface-container-highest rounded-full overflow-hidden flex">
                    <div id="adv-sym-left" class="h-full bg-primary transition-all duration-1000" style="width: 50%"></div>
                    <div id="adv-sym-right" class="h-full bg-secondary transition-all duration-1000" style="width: 50%"></div>
                </div>
                <div class="text-xl font-bold text-on-surface" id="adv-sym-score">--% Match</div>
                <p class="text-[10px] text-error hidden" id="adv-sym-warning">Asymmetry Detected</p>
            </div>
        </div>

        <!-- 4. Scan Quality Score -->
        <div class="glass-panel p-6 rounded-2xl">
            <h4 class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">4. Scan Quality</h4>
            <div class="flex flex-col items-center justify-center h-48 relative">
                <div class="relative w-32 h-16 overflow-hidden">
                    <div class="absolute top-0 left-0 w-32 h-32 rounded-full border-[12px] border-surface-container-highest"></div>
                    <div id="adv-quality-gauge" class="absolute top-0 left-0 w-32 h-32 rounded-full border-[12px] border-primary border-b-transparent border-r-transparent -rotate-45 transition-transform duration-1000"></div>
                </div>
                <div class="absolute bottom-6 flex flex-col items-center">
                    <span class="text-3xl font-bold text-on-surface" id="adv-quality-score">--</span>
                    <span class="text-[12px] font-bold text-on-surface-variant uppercase" id="adv-quality-label">Pending</span>
                </div>
            </div>
        </div>

        <!-- 3. Tumor Heatzone Map -->
        <div class="glass-panel p-6 rounded-2xl">
            <h4 class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">3. Tumor Heatzone Map</h4>
            <div class="grid grid-cols-2 grid-rows-2 gap-1 h-48 bg-surface-container-highest p-1 rounded-xl">
                <div class="rounded-lg flex flex-col items-center justify-center transition-colors duration-1000" id="adv-hz-tl">
                    <span class="text-[10px] text-on-surface-variant">Top-Left</span>
                    <span class="font-bold text-on-surface" id="adv-hz-tl-val">--%</span>
                </div>
                <div class="rounded-lg flex flex-col items-center justify-center transition-colors duration-1000" id="adv-hz-tr">
                    <span class="text-[10px] text-on-surface-variant">Top-Right</span>
                    <span class="font-bold text-on-surface" id="adv-hz-tr-val">--%</span>
                </div>
                <div class="rounded-lg flex flex-col items-center justify-center transition-colors duration-1000" id="adv-hz-bl">
                    <span class="text-[10px] text-on-surface-variant">Bottom-Left</span>
                    <span class="font-bold text-on-surface" id="adv-hz-bl-val">--%</span>
                </div>
                <div class="rounded-lg flex flex-col items-center justify-center transition-colors duration-1000" id="adv-hz-br">
                    <span class="text-[10px] text-on-surface-variant">Bottom-Right</span>
                    <span class="font-bold text-on-surface" id="adv-hz-br-val">--%</span>
                </div>
            </div>
        </div>

        <!-- 5. Lobe Detection Indicator -->
        <div class="glass-panel p-6 rounded-2xl">
            <h4 class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">5. Lobe Detection</h4>
            <div class="flex flex-col items-center justify-center h-48 gap-4">
                <span class="material-symbols-outlined text-6xl text-primary/30" id="adv-lobe-icon">psychology</span>
                <div class="text-center">
                    <div class="text-[12px] text-on-surface-variant uppercase mb-1">Estimated Affected Region</div>
                    <div class="text-xl font-bold text-primary" id="adv-lobe-name">Pending Scan</div>
                </div>
            </div>
        </div>

        <!-- 6. Confidence Breakdown Radar -->
        <div class="glass-panel p-6 rounded-2xl lg:col-span-2">
            <h4 class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">6. Confidence Breakdown Radar</h4>
            <div class="relative h-48 w-full flex items-center justify-center">
                <canvas id="adv-chart-radar"></canvas>
            </div>
        </div>

        <!-- 7. Risk Score Meter -->
        <div class="glass-panel p-6 rounded-2xl">
            <h4 class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">7. Clinical Risk Score</h4>
            <div class="flex flex-col items-center justify-center h-48 relative">
                <div class="relative w-32 h-32 rounded-full border-[8px] border-surface-container-highest flex items-center justify-center shadow-[inset_0_0_20px_rgba(0,0,0,0.5)]">
                    <div class="absolute inset-0 rounded-full border-[8px] border-error border-l-transparent border-t-transparent -rotate-45 transition-transform duration-1000" id="adv-risk-ring"></div>
                    <div class="flex flex-col items-center">
                        <span class="text-4xl font-bold text-on-surface" id="adv-risk-score">--</span>
                        <span class="text-[10px] font-bold text-on-surface-variant uppercase mt-1">Score</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 8. Before/After Timeline -->
        <div class="glass-panel p-6 rounded-2xl lg:col-span-3">
            <h4 class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">8. Patient Confidence Timeline</h4>
            <div class="relative h-48 w-full flex items-center justify-center">
                <canvas id="adv-chart-timeline"></canvas>
            </div>
        </div>
    </div>
"""

# Insert before "Recent Predictions Table"
insert_target = '<!-- Recent Predictions Table -->'
if insert_target in html:
    html = html.replace(insert_target, new_analytics_html + '\n    ' + insert_target)
    with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Injected advanced analytics HTML")
else:
    print("Could not find insert target")
