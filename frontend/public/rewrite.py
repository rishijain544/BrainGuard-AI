import re

with open('d:/brain_tumour_prediction/public/predict.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add vanilla-tilt to head
if "vanilla-tilt" not in html:
    html = html.replace('</head>', '    <script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.1/vanilla-tilt.min.js"></script>\n</head>')

# 2. Extract Nav
nav_match = re.search(r'<!-- Navigation Tabs -->.*?</nav>', html, re.DOTALL)
if nav_match:
    nav_html = nav_match.group(0).replace('style="text-decoration:none; color:inherit; margin-right:16px;"', '')
    nav_html = nav_html.replace('class="main-nav"', 'class="main-nav" style="flex-direction: column;"')
    html = html.replace(nav_match.group(0), '') # Remove from header

# 3. Create the new Sidebar and insert at the start of page-dashboard
sidebar_html = f'''<!-- LEFT SIDEBAR -->
        <aside class="sidebar dashboard-card" data-tilt data-tilt-max="2" data-tilt-glare data-tilt-max-glare="0.1">
            {nav_html if nav_match else '<!-- Nav Not Found -->'}
            <div style="flex-grow: 1;"></div>
            <div class="user-profile" style="display: flex; gap: 12px; align-items: center; padding-top: 16px; border-top: 1px solid var(--border-color);">
                <img src="https://i.pravatar.cc/150?img=11" style="width: 40px; border-radius: 50%;">
                <div>
                    <div style="font-weight: 700; font-size: 13px;">Dr. Adam Bridges</div>
                    <div style="font-size: 11px; color: var(--text-secondary);">Neurologist</div>
                </div>
            </div>
        </aside>
'''
if "<!-- LEFT SIDEBAR -->" not in html:
    html = html.replace('<main class="app-main-grid" id="page-dashboard">', '<main class="app-main-grid" id="page-dashboard">\n' + sidebar_html)

# 4. Add data-tilt to all dashboard cards
html = html.replace('class="dashboard-card ', 'class="dashboard-card" data-tilt data-tilt-max="2" data-tilt-glare data-tilt-max-glare="0.1" class="dashboard-card ')
html = html.replace('class="dashboard-card"', 'class="dashboard-card" data-tilt data-tilt-max="2" data-tilt-glare data-tilt-max-glare="0.1"')

# Fix multiple class attributes issue
html = re.sub(r'class="dashboard-card" (data-tilt.*?) class="dashboard-card (.*?)"', r'class="dashboard-card \2" \1', html)

# 5. Make sure the app-container has perspective-mode
html = html.replace('<div class="app-container">', '<div class="app-container perspective-mode">')

with open('d:/brain_tumour_prediction/public/predict.html', 'w', encoding='utf-8') as f:
    f.write(html)
