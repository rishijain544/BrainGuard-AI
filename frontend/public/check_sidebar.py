import re
with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

sidebar_match = re.search(r'<aside[^>]*>', html)
if sidebar_match:
    print('Sidebar tag:', sidebar_match.group(0))

main_match = re.search(r'<div[^>]*ml-64[^>]*>', html)
if main_match:
    print('Main wrapper:', main_match.group(0))
else:
    wrapper = re.search(r'<div[^>]*flex-1[^>]*>', html)
    if wrapper:
        print('Flex wrapper:', wrapper.group(0))
