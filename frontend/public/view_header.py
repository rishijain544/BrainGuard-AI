with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
    start = html.find('<header')
    if start == -1: start = html.find('<div class="app-header')
    print(html[start-100:start+500])
