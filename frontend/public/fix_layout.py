with open('d:/brain_tumour_prediction/public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix cache busting
html = html.replace('href="styles.css"', 'href="styles.css?v=4"')

# 2. Fix "How It Works" button class error
html = html.replace('class="nav-tab" data-page="about" class="btn btn-secondary btn-large"', 'class="nav-tab btn btn-secondary btn-large" data-page="about"')

# 3. Fix the app-main-grid layout to be Top/Bottom instead of Left/Right
new_grid = '''<div class="app-main-grid" style="display: flex; flex-direction: column; gap: 24px; max-width: 1200px; margin: 0 auto;">

            <!-- TOP ROW (Upload & Patient Info) -->
            <section class="grid-column-left" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; width: 100%;">'''

html = html.replace('<div class="app-main-grid">\n\n            <!-- LEFT COLUMN -->\n            <section class="grid-column-left">', new_grid)

# 4. Fix grid-column-right to take full width
html = html.replace('<section class="grid-column-right">', '<section class="grid-column-right" style="width: 100%;">')

# 5. Add inline CSS to force analytics charts to behave!
css_fix = '''<style>
.chart-body canvas {
    width: 100% !important;
    max-height: 280px !important;
    object-fit: contain;
}
.app-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
}
</style>
</head>'''
html = html.replace('</head>', css_fix)

with open('d:/brain_tumour_prediction/public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
