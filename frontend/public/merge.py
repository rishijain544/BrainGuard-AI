import re

# Read both files
with open('d:/brain_tumour_prediction/public/index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()
    
with open('d:/brain_tumour_prediction/public/predict.html', 'r', encoding='utf-8') as f:
    predict_html = f.read()

# Extract dashboard content from predict.html
dash_match = re.search(r'(<main id="page-dashboard".*?</main>)', predict_html, re.DOTALL)
if dash_match:
    dashboard_content = dash_match.group(1)
    
    # We also need the other hidden pages (history, analytics) and modals
    pages_match = re.search(r'(<main id="page-history".*?</body>)', predict_html, re.DOTALL)
    if pages_match:
        other_content = pages_match.group(1).replace('</body>', '')
    else:
        other_content = ''
        
    # Replace the Hero section CTA to scroll down instead of linking to predict.html
    index_html = index_html.replace('href="predict.html"', 'href="#dashboard-section"')
    
    # Insert the dashboard right after the Hero section
    # Let's insert it before the FEATURES SECTION
    footer_pos = index_html.find('<!-- FEATURES SECTION -->')
    
    combined_html = index_html[:footer_pos] + '\n<!-- DASHBOARD SPA -->\n<div id="dashboard-section" class="dashboard-wrapper">\n' + dashboard_content + '\n' + other_content + '\n</div>\n' + index_html[footer_pos:]
    
    # Add JS scripts before </body>
    if '<script src="app.js"></script>' not in combined_html:
        combined_html = combined_html.replace('</body>', '    <script src="app.js"></script>\n</body>')
        
    if 'vanilla-tilt.min.js' not in combined_html:
        combined_html = combined_html.replace('</head>', '    <script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.1/vanilla-tilt.min.js"></script>\n</head>')
        
    if 'chart.umd.min.js' not in combined_html:
        combined_html = combined_html.replace('</head>', '    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>\n</head>')

    with open('d:/brain_tumour_prediction/public/index.html', 'w', encoding='utf-8') as f:
        f.write(combined_html)
        print('Unified index.html created.')
