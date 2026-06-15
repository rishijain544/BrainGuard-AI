import re

html_path = r'd:\brain_tumour_prediction\frontend\public\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Rename Cerebro AI to Brain Guard AI
html = html.replace('Cerebro AI', 'Brain Guard AI')
html = html.replace('Cerebro', 'BrainGuard')

# 2. Remove Doctor Profile
# The doctor profile is around line 240:
# <div class="flex flex-col items-end mr-4">
# <span class="font-title-md text-title-md text-primary font-bold">Dr. Julian Vane</span>
# <span class="text-[10px] uppercase tracking-widest text-on-surface-variant/70">Chief Neurologist</span>
# </div>
# <button class="w-10 h-10 rounded-full glass-panel flex items-center justify-center text-on-surface-variant hover:text-primary transition-colors">
# <span class="material-symbols-outlined">notifications</span>
# </button>
# <div class="w-12 h-12 rounded-full border-2 border-primary-container p-0.5 shadow-lg shadow-primary/20 overflow-hidden">
# <img alt="Dr. Julian Vane" ...>
# </div>

doctor_pattern = r'<div class="flex items-center gap-4">.*?<div class="flex flex-col items-end mr-4">.*?<img alt="Dr\. Julian Vane".*?</div>.*?</div>'
# Instead of regex which can be tricky across newlines, let's replace manually or use a more specific regex with DOTALL.
html = re.sub(r'<div class="flex flex-col items-end mr-4">.*?<span class="font-title-md text-title-md text-primary font-bold">Dr\. Julian Vane</span>.*?</div>', '', html, flags=re.DOTALL)
html = re.sub(r'<div class="w-12 h-12 rounded-full border-2 border-primary-container p-0\.5 shadow-lg shadow-primary/20 overflow-hidden">.*?<img alt="Dr\. Julian Vane".*?</div>', '', html, flags=re.DOTALL)


# 3. Wire Sidebar Links
# Sidebar has:
# <a class="... text-primary-fixed-dim border-r-2 border-primary-container ..." href="#"> <span ...>dashboard</span> Dashboard </a>
# <a class="... text-on-surface-variant ..." href="#"> <span ...>psychology_alt</span> Patient Scans </a> (let's wire this to history)
# <a class="... text-on-surface-variant ..." href="#"> <span ...>biotech</span> Neural Analysis </a> (let's wire this to analytics)
# <a class="... text-on-surface-variant ..." href="#"> <span ...>description</span> Clinic Reports </a>
# Let's replace href="#" with href="javascript:void(0)" and add onclick handlers.

# Find the nav block inside aside
nav_start = html.find('<nav class="flex-1 space-y-2">')
if nav_start != -1:
    nav_end = html.find('</nav>', nav_start)
    nav_block = html[nav_start:nav_end]
    
    # Wire Dashboard
    nav_block = nav_block.replace('Dashboard\n            </a>', 'Dashboard\n            </a>').replace('href="#">', 'href="javascript:void(0)" onclick="switchPage(\'dashboard\')">', 1)
    # Wire Patient Scans to History
    nav_block = nav_block.replace('Patient Scans\n            </a>', 'Past History\n            </a>').replace('href="#">', 'href="javascript:void(0)" onclick="switchPage(\'history\')">', 1)
    # Wire Neural Analysis to Analytics
    nav_block = nav_block.replace('Neural Analysis\n            </a>', 'Analytics\n            </a>').replace('href="#">', 'href="javascript:void(0)" onclick="switchPage(\'analytics\')">', 1)
    
    html = html[:nav_start] + nav_block + html[nav_end:]

# Add switchPage helper at the bottom if not exists
switch_page_script = """
    <script>
        function switchPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
            const target = document.getElementById('page-' + pageId);
            if(target) {
                target.classList.remove('hidden');
            }
        }
    </script>
"""
if 'function switchPage(' not in html:
    html = html.replace('</body>', switch_page_script + '</body>')


# 4. Wire Export Report button
# Find Export Report
html = html.replace('Export Report\n                    </button>', 'Export Report\n                    </button>').replace('<button class="glass-panel px-4 py-2 rounded-lg flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors text-body-sm">\n<span class="material-symbols-outlined text-[18px]">file_download</span>\n                        Export Report', '<button class="glass-panel px-4 py-2 rounded-lg flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors text-body-sm" id="ui-export-btn" onclick="document.getElementById(\'download-pdf-btn\').click()">\n<span class="material-symbols-outlined text-[18px]">file_download</span>\n                        Export Report')


# 5. Fix analyze-btn loading state. The original app.js looks for '#analyze-btn' and changes its content. 
# In new UI, it's `<span class="btn-text">Initiate Surgery Planning</span><span class="btn-loader hidden"> 🔄</span>`
# Let's change the text of analyze-btn to 'Scan & Analyze'
html = html.replace('Initiate Surgery Planning', 'Scan & Analyze')


with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html modifications completed.")

