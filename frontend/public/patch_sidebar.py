import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

btn_html = '''
<div class="mt-auto space-y-2 border-t border-white/5 pt-6">
    <button onclick="toggleSidebar()" class="flex w-full items-center justify-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:bg-white/5 hover:text-primary transition-all duration-300">
        <span class="material-symbols-outlined" id="sidebar-toggle-icon">keyboard_double_arrow_left</span>
        <span class="sidebar-text font-body-sm">Collapse Sidebar</span>
    </button>
</div>
'''

idx = html.find('</aside>')
if idx != -1:
    mt_auto_idx = html.find('<div class="mt-auto space-y-2 border-t border-white/5 pt-6">')
    if mt_auto_idx != -1:
        end_div = html.find('</div>', mt_auto_idx)
        if end_div != -1:
            html = html[:mt_auto_idx] + btn_html + html[end_div+6:]
    else:
        html = html[:idx] + btn_html + html[idx:]

css = '''
<style>
    body.sidebar-collapsed aside {
        width: 5rem !important;
    }
    body.sidebar-collapsed .sidebar-text,
    body.sidebar-collapsed .sidebar-header-text {
        display: none !important;
    }
    body.sidebar-collapsed main.ml-72,
    body.sidebar-collapsed main.page.ml-72 {
        margin-left: 5rem !important;
    }
    body.sidebar-collapsed header.fixed.top-0 {
        width: calc(100% - 5rem) !important;
    }
    body.sidebar-collapsed aside nav a {
        justify-content: center;
        padding-left: 0;
        padding-right: 0;
    }
    aside, main, header, .sidebar-text, .sidebar-header-text {
        transition: all 0.3s ease;
    }
</style>
'''
head_idx = html.find('</head>')
html = html[:head_idx] + css + html[head_idx:]

html = html.replace('<div>\n<h1 class="font-headline-lg', '<div class="sidebar-header-text">\n<h1 class="font-headline-lg')

nav_links = re.findall(r'<a.*?<span class="material-symbols-outlined">[^<]+</span>\s*(.*?)\s*</a>', html, re.DOTALL)
for link_text in set(nav_links):
    if link_text.strip() and "switchPage" in link_text:
        continue

html = html.replace('Dashboard\n            </a>', '<span class="sidebar-text">Dashboard</span>\n            </a>')
html = html.replace('Past History\n            </a>', '<span class="sidebar-text">Past History</span>\n            </a>')
html = html.replace('Analytics\n            </a>', '<span class="sidebar-text">Analytics</span>\n            </a>')
html = html.replace('Clinic Reports\n            </a>', '<span class="sidebar-text">Clinic Reports</span>\n            </a>')

html = html.replace('New Scan Analysis\n        </button>', '<span class="sidebar-text">New Scan Analysis</span>\n        </button>')

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
