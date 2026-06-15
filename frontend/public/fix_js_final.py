import re

js_path = r'd:\brain_tumour_prediction\frontend\public\app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Remove all instances of the duplicated Image Analysis block
block_start = r'// ──────────────────────────────────────────────────────────────────────────\s*// IMAGE PIXEL ANALYSIS \(CLIENT SIDE\)'
# We will just split by block_start
parts = re.split(block_start, js)

clean_js = parts[0]
for p in parts[1:]:
    # Find where the block ends. It ends after the renderCurrentScanAnalytics function definition.
    # We can look for `    }\n    }\n'''` or similar, but simpler:
    # Just remove everything up to the next `// --- NEW UI UPDATES ---` or another recognizable function.
    pass

# Actually, it's easier to use a more robust approach.
# Since the file is completely messed up, let's just restore the original `app.js` if it exists in the transcript or write a regex that matches the exact duplicated string.

# Wait, `patch_app.py` defines the exact string that was inserted!
with open(r'd:\brain_tumour_prediction\frontend\public\patch_app.py', 'r', encoding='utf-8') as f:
    patch_script = f.read()

# Extract the exact string that was inserted
start_marker = "image_analysis_code = '''"
end_marker = "'''"
if start_marker in patch_script:
    inserted_code = patch_script.split(start_marker)[1].split(end_marker)[0]
    
    # Remove all instances of inserted_code
    # Because of indentation or slight changes, we might need to remove it carefully.
    js = js.replace(inserted_code, "")
    
    # Add it back exactly ONCE at the end of the file
    js += "\n" + inserted_code

# Remove the duplicated try { renderCurrentScanAnalytics(imagePreview); } catch(e) { console.error("Analytics Error", e); }
render_call = 'try { renderCurrentScanAnalytics(imagePreview); } catch(e) { console.error("Analytics Error", e); }'
js = js.replace(render_call, "")

# We also had `--- NEW UI UPDATES ---` which might be duplicated.
ui_update_start = "// --- NEW UI UPDATES ---"
ui_update_end = "// --- END NEW UI UPDATES ---"
# Remove all of them
while ui_update_start in js:
    s = js.find(ui_update_start)
    e = js.find(ui_update_end) + len(ui_update_end)
    if e > s:
        js = js[:s] + js[e:]
    else:
        break

# Now, we need to insert the render call inside displayAnalysisResults.
# find `function displayAnalysisResults`
s = js.find('function displayAnalysisResults')
if s != -1:
    # find the end of this function. Just insert our new code right after it's defined, or at the end of the block.
    # Better yet, insert it right before the closing brace of displayAnalysisResults.
    pass

# To be safe, let's just append a wrapper function or redefine the UI updates.
patch_code = """
        // --- NEW UI UPDATES ---
        try {
            const confPct = (e.result.ensemble_confidence * 100).toFixed(1);
            if(document.getElementById('gauge-value')) document.getElementById('gauge-value').innerText = confPct;
            if(document.getElementById('gauge-fill')) document.getElementById('gauge-fill').setAttribute('stroke-dasharray', confPct + ', 100');
            
            const isTumor = e.result.ensemble_prediction !== 'notumor';
            
            if(document.getElementById('ui-tumor-volume')) {
                let vol = '--';
                if(document.getElementById('ana-tumor-area')) {
                    vol = (parseInt(document.getElementById('ana-tumor-area').innerText) / 100).toFixed(1);
                }
                document.getElementById('ui-tumor-volume').innerText = isTumor ? vol : '0.0';
            }
            
            if(document.getElementById('ui-malignancy-risk')) {
                document.getElementById('ui-malignancy-risk').innerText = isTumor ? (confPct > 90 ? 'High' : (confPct > 70 ? 'Moderate' : 'Low')) : 'None';
            }
            if(document.getElementById('ui-location')) {
                if(document.getElementById('ana-lobe')) {
                    document.getElementById('ui-location').innerText = isTumor ? document.getElementById('ana-lobe').innerText : 'N/A';
                }
            }
            
            if(document.getElementById('ui-contrast')) document.getElementById('ui-contrast').innerText = isTumor ? 'Heterogeneous' : 'N/A';
            if(document.getElementById('ui-edema')) document.getElementById('ui-edema').innerText = isTumor ? 'Present' : 'Negative';
            if(document.getElementById('ui-vascular')) {
                const el = document.getElementById('ui-vascular');
                if (isTumor && confPct > 85) {
                    el.innerText = 'Possible';
                    el.className = 'text-on-error font-mono-data px-2 py-1 bg-error/10 rounded text-[12px]';
                } else {
                    el.innerText = 'Negative';
                    el.className = 'text-on-surface font-mono-data px-2 py-1 bg-white/5 rounded text-[12px]';
                }
            }
            
            if(e.result.gradcam_overlay_base64 && e.result.gradcam_overlay_base64.length > 50) {
                if(document.getElementById('image-preview')) {
                    document.getElementById('image-preview').src = e.result.gradcam_overlay_base64;
                }
            }
        } catch(err) {
            console.error("Error updating new UI:", err);
        }
        // --- END NEW UI UPDATES ---
"""

js = js.replace('document.getElementById("results-container").innerHTML = \'\';', 'document.getElementById("results-container").innerHTML = \'\';\n' + render_call + '\n' + patch_code)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("js cleaned!")
