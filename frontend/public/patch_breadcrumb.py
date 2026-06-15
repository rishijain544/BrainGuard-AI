with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<span class="text-primary font-bold font-body-sm">Case #X4AD2-92</span>', '<span class="text-primary font-bold font-body-sm" id="ui-case-id">Case #Pending</span>')

with open('d:/brain_tumour_prediction/frontend/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
