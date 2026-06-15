import re

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

analytics_start = html.find('<div id="page-analytics"')
if analytics_start != -1:
    analytics_end = html.find('</div>\n    <div id="page-history"', analytics_start)
    if analytics_end == -1: analytics_end = html.find('<div id="page-history"', analytics_start)
    print("=== ANALYTICS SECTION ===")
    print(html[analytics_start:analytics_end])

history_start = html.find('<div id="page-history"')
if history_start != -1:
    history_end = html.find('</div>\n    <div id="page-about"', history_start)
    if history_end == -1: history_end = html.find('<div id="page-about"', history_start)
    print("=== HISTORY SECTION ===")
    print(html[history_start:history_end])
