with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_analytics = html.find('id="page-analytics"')
if start_analytics != -1:
    print('ANALYTICS FOUND:')
    print(html[start_analytics:start_analytics+1000])
    
start_history = html.find('id="page-history"')
if start_history != -1:
    print('\nHISTORY FOUND:')
    print(html[start_history:start_history+1000])
