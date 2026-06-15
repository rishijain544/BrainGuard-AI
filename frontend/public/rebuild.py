import re

with open('d:/brain_tumour_prediction/public/predict.html', 'r', encoding='utf-8') as f:
    predict = f.read()
    
# Extract dashboard sections
dash_match = re.search(r'(<main id="page-dashboard".*?</main>)', predict, re.DOTALL)
page_dashboard = dash_match.group(1) if dash_match else ''

history_match = re.search(r'(<main id="page-history".*?</main>)', predict, re.DOTALL)
page_history = history_match.group(1) if history_match else ''

analytics_match = re.search(r'(<main id="page-analytics".*?</main>)', predict, re.DOTALL)
page_analytics = analytics_match.group(1) if analytics_match else ''

modals_match = re.search(r'(<!-- SETTINGS MODAL -->.*?</div>)', predict, re.DOTALL)
modals = modals_match.group(1) if modals_match else ''

detail_modal_match = re.search(r'(<!-- SCAN DETAIL MODAL -->.*?</div>)', predict, re.DOTALL)
detail_modal = detail_modal_match.group(1) if detail_modal_match else ''

# Extract About content from about.html
with open('d:/brain_tumour_prediction/public/about.html', 'r', encoding='utf-8') as f:
    about = f.read()

about_match = re.search(r'<main class="container about-container">(.*?)</main>', about, re.DOTALL)
about_content = about_match.group(1) if about_match else ''
page_about = f'''
    <main id="page-about" class="page hidden dashboard-wrapper">
        <div class="container" style="max-width: 1000px; padding: 40px 20px;">
            {about_content}
        </div>
    </main>
'''

# Create Contact Content
page_contact = '''
    <main id="page-contact" class="page hidden dashboard-wrapper">
        <div class="container" style="max-width: 800px; padding: 40px 20px;">
            <div class="dashboard-card" style="text-align: center; padding: 40px;">
                <h1 style="font-family: var(--font-header); margin-bottom: 16px;">Contact Us</h1>
                <p style="color: var(--text-secondary); margin-bottom: 32px;">Reach out to the BrainGuard AI team for support or inquiries.</p>
                <form class="patient-form" style="max-width: 500px; margin: 0 auto; text-align: left;">
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label>Your Name</label>
                        <input type="text" placeholder="Dr. Jane Smith">
                    </div>
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label>Email Address</label>
                        <input type="email" placeholder="jane.smith@hospital.org">
                    </div>
                    <div class="form-group" style="margin-bottom: 24px;">
                        <label>Message</label>
                        <textarea rows="4" style="background: #09090b; border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 14px; color: var(--text-primary); font-family: var(--font-body); resize: vertical;"></textarea>
                    </div>
                    <button type="button" class="primary-btn glow-effect" style="width: 100%;">Send Message</button>
                </form>
            </div>
        </div>
    </main>
'''

# We need to prepend the Hero section to page_dashboard!
with open('d:/brain_tumour_prediction/public/index.html', 'r', encoding='utf-8') as f:
    old_index = f.read()

hero_match = re.search(r'(<!-- HERO SECTION -->.*?)</section>', old_index, re.DOTALL)
hero_content = hero_match.group(1) + '</section>' if hero_match else ''

# Replace CTA in hero
hero_content = hero_content.replace('href="predict.html"', 'href="#mri-scan" onclick="document.getElementById(\'mri-scan\').scrollIntoView({behavior:\'smooth\'})"')
hero_content = hero_content.replace('href="about.html"', 'href="#" class="nav-tab" data-page="about"')

# Rebuild page_dashboard
page_dashboard = page_dashboard.replace('<main id="page-dashboard" class="page active">', f'''<main id="page-dashboard" class="page active">
{hero_content}
<div id="mri-scan" style="padding-top: 40px;"></div>
''')

# Now build full index.html
new_index = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BrainGuard AI | Next-Generation Neurological Diagnostics</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="landing.css">
    <link rel="stylesheet" href="styles.css">
    <link rel="icon" href="favicon.svg" type="image/svg+xml">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.1/vanilla-tilt.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body class="landing-body">
    
    <!-- HEADER -->
    <header class="site-header">
        <div class="container header-container">
            <a href="#" class="brand-logo nav-tab" data-page="dashboard" style="text-decoration:none;">
                <img src="logo.png" alt="BrainGuard AI Logo" class="logo-img" style="height: 48px; width: auto; object-fit: contain;">
                <span class="brand-text" style="display: none;">BrainGuard<span class="brand-highlight">AI</span></span>
            </a>
            <nav class="site-nav">
                <button class="nav-tab active" data-page="dashboard">Home / Dashboard</button>
                <button class="nav-tab" data-page="analytics">Analytics</button>
                <button class="nav-tab" data-page="history">Past History</button>
                <button class="nav-tab" data-page="about">About</button>
                <button class="nav-tab" data-page="contact">Contact Us</button>
            </nav>
            <div class="header-controls">
                <div id="status-badge" class="status-badge disconnected">
                    <span class="status-dot"></span>
                    <span class="status-text">DISCONNECTED</span>
                    <span id="device-info" class="device-info hidden"></span>
                </div>
            </div>
        </div>
    </header>

    <div style="padding-top: 72px;">
        {page_dashboard}
        {page_analytics}
        {page_history}
        {page_about}
        {page_contact}
    </div>

    <!-- FOOTER -->
    <footer class="site-footer">
        <div class="container footer-bottom text-center">
            <p>&copy; 2026 BrainGuard AI. For demonstration and research purposes only.</p>
        </div>
    </footer>
    
    {modals}
    {detail_modal}
    <script src="app.js"></script>
</body>
</html>'''

with open('d:/brain_tumour_prediction/public/index.html', 'w', encoding='utf-8') as f:
    f.write(new_index)
