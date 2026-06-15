with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

models_ui = '''
<!-- Explicit Model Breakdowns -->
<div class="grid grid-cols-3 gap-4 mt-4">
    <div class="glass-panel p-4 rounded-xl border-t-2 border-primary/50 text-center shadow-lg">
        <span class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">CNN Model</span>
        <div class="text-xl font-bold text-on-surface mt-1" id="ui-cnn-conf">--%</div>
        <div class="text-[10px] text-primary mt-1 uppercase" id="ui-cnn-pred">Pending</div>
    </div>
    <div class="glass-panel p-4 rounded-xl border-t-2 border-secondary/50 text-center shadow-lg">
        <span class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">ResNet50</span>
        <div class="text-xl font-bold text-on-surface mt-1" id="ui-resnet-conf">--%</div>
        <div class="text-[10px] text-secondary mt-1 uppercase" id="ui-resnet-pred">Pending</div>
    </div>
    <div class="glass-panel p-4 rounded-xl border-t-2 border-[#ff00a0]/50 text-center shadow-lg">
        <span class="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Hybrid ViT</span>
        <div class="text-xl font-bold text-on-surface mt-1" id="ui-vit-conf">--%</div>
        <div class="text-[10px] text-[#ff00a0] mt-1 uppercase" id="ui-vit-pred">Pending</div>
    </div>
</div>
'''

target = '<div class="glass-panel p-5 rounded-xl border-l-4 border-secondary shadow-lg shadow-secondary/5">'
idx = html.find(target)
if idx != -1:
    end_idx = html.find('</div>', html.find('</div>', html.find('</div>', idx) + 1) + 1) + 6
    insert_idx = html.find('</div>', end_idx) + 6
    html = html[:insert_idx] + models_ui + html[insert_idx:]

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
