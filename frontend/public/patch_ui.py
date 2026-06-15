import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Clean up Nav Bar
nav_links_to_remove = [
    r'<a[^>]*href="#"[^>]*>\s*<span class="material-symbols-outlined">settings</span>\s*System Settings\s*</a>',
    r'<a[^>]*href="#"[^>]*>\s*<span class="material-symbols-outlined">help_outline</span>\s*Support\s*</a>',
    r'<a[^>]*href="#"[^>]*>\s*<span class="material-symbols-outlined">logout</span>\s*Logout\s*</a>'
]
for pattern in nav_links_to_remove:
    html = re.sub(pattern, '', html)

# Replace `#` with `javascript:void(0)` and add onclick for Clinic Reports
html = html.replace(
    '''<a class="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:bg-white/5 hover:text-primary transition-all duration-300 font-body-sm" href="#">
<span class="material-symbols-outlined">description</span>
                Clinic Reports
            </a>''',
    '''<a class="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:bg-white/5 hover:text-primary transition-all duration-300 font-body-sm" href="javascript:void(0)" onclick="switchPage('reports')">
<span class="material-symbols-outlined">description</span>
                Clinic Reports
            </a>'''
)

# 2. Add Patient Details form and replace Scan History Bento
patient_form = '''<!-- Patient Details & Upload -->
<div class="glass-panel p-6 rounded-2xl mb-4 mt-2">
    <div class="text-primary font-bold text-[12px] uppercase tracking-widest mb-4 border-b border-white/5 pb-2">Patient Details & Scan Upload</div>
    <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
            <label class="text-[10px] text-on-surface-variant font-bold uppercase tracking-widest block mb-1">Patient Name</label>
            <input type="text" id="patient-name" class="w-full bg-surface-container-highest border-none rounded-lg px-3 py-2 text-body-sm text-on-surface focus:ring-1 focus:ring-primary/50 transition-all" placeholder="Enter name">
        </div>
        <div>
            <label class="text-[10px] text-on-surface-variant font-bold uppercase tracking-widest block mb-1">Patient ID</label>
            <input type="text" id="patient-id" class="w-full bg-surface-container-highest border-none rounded-lg px-3 py-2 text-body-sm text-on-surface focus:ring-1 focus:ring-primary/50 transition-all" placeholder="e.g. PT-12345">
        </div>
        <div>
            <label class="text-[10px] text-on-surface-variant font-bold uppercase tracking-widest block mb-1">Age</label>
            <input type="number" id="patient-age" class="w-full bg-surface-container-highest border-none rounded-lg px-3 py-2 text-body-sm text-on-surface focus:ring-1 focus:ring-primary/50 transition-all" placeholder="Years">
        </div>
        <div>
            <label class="text-[10px] text-on-surface-variant font-bold uppercase tracking-widest block mb-1">Scan Date</label>
            <input type="date" id="scan-date" class="w-full bg-surface-container-highest border-none rounded-lg px-3 py-2 text-body-sm text-on-surface focus:ring-1 focus:ring-primary/50 transition-all">
        </div>
    </div>
    <div class="glass-panel p-4 rounded-xl border-dashed border-primary/30 flex flex-col items-center justify-center gap-2 group hover:border-primary/80 transition-all cursor-pointer bg-primary/5" id="dropzone" onclick="document.getElementById('file-input').click()">
        <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-on-primary transition-colors">
            <span class="material-symbols-outlined">upload_file</span>
        </div>
        <span class="text-[12px] font-bold text-primary">Click or drag image to upload</span>
    </div>
    <input type="file" id="file-input" accept="image/*" class="hidden">
</div>'''

# We need to replace the entire <div class="grid grid-cols-3 gap-4"> block inside col-span-7
start_bento = html.find('<!-- Scan History Bento -->')
if start_bento != -1:
    end_bento = html.find('</div>\n</div>\n<!-- Right Column', start_bento)
    if end_bento != -1:
        # replace everything from start_bento to end_bento with patient_form
        html = html[:start_bento] + patient_form + '\n' + html[end_bento:]

# 3. Add UI diagnosis subtitle
subtitle_orig = '<p class="text-body-sm text-on-surface-variant">High precision neural mapping complete. Lesion detected with high morphological matching.</p>'
subtitle_new = '<p id="ui-diagnosis-subtitle" class="text-body-sm text-on-surface-variant">High precision neural mapping complete. Awaiting scan.</p>'
html = html.replace(subtitle_orig, subtitle_new)

# 4. Clinic Reports Page
reports_page = '''
<main class="page hidden" id="page-reports">
    <div class="pt-24 px-gutter pb-gutter">
        <div class="glass-panel p-10 rounded-2xl max-w-3xl mx-auto text-center mt-10">
            <span class="material-symbols-outlined text-[64px] text-primary mb-4">picture_as_pdf</span>
            <h2 class="text-headline-lg font-bold text-on-surface mb-2">Clinical Report Generator</h2>
            <p class="text-body-lg text-on-surface-variant mb-8">Download a comprehensive, verifiable PDF report for the currently active scan analysis.</p>
            
            <button id="ui-export-btn-big" class="bg-primary-container text-on-primary-container px-8 py-4 rounded-xl font-bold flex items-center justify-center gap-3 active:scale-95 transition-transform shadow-lg shadow-primary/30 mx-auto w-full max-w-md">
                <span class="material-symbols-outlined">file_download</span>
                Generate Clinical PDF Report
            </button>
        </div>
    </div>
</main>
'''

# insert before id="page-about"
idx_about = html.find('<main class="page hidden dashboard-wrapper" id="page-about">')
if idx_about != -1:
    html = html[:idx_about] + reports_page + html[idx_about:]


# 5. Make icons smaller
# The huge empty state SVG has height="48" width="48". We'll make it height="32" width="32".
html = html.replace('height="48" viewbox="0 0 64 64" width="48"', 'height="32" viewbox="0 0 64 64" width="32"')

# Save
with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
