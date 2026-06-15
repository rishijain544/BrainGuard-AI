import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the redundant inner <main>
html = html.replace('<main class="page active ml-72 min-h-screen relative" id="page-dashboard"><main class="ml-72 min-h-screen relative">', '<main class="page active ml-72 min-h-screen relative" id="page-dashboard">')

# Wait, does the extra </main> exist?
# If so, let's just let it be, or remove the last </main> inside page-dashboard.
# Since it's invalid HTML, browsers might auto-correct or ignore the extra </main>.
# Let's remove the first </main></main> we find and replace with </main>
html = html.replace('</main>\n</main>', '</main>')

# 2. Remove the outer header
header1 = re.search(r'<!-- HEADER -->\s*<header.*?</header>\s*<div style="padding-top: 72px;">', html, re.DOTALL)
if header1:
    html = html.replace(header1.group(0), '')

# 3. Remove Share/Export buttons
buttons = re.search(r'<div class="flex gap-3">\s*<button.*?Share Findings.*?</button>\s*<button.*?Export Report.*?</button>\s*</div>', html, re.DOTALL)
if buttons:
    html = html.replace(buttons.group(0), '')

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
