import re

js_path = r'd:\brain_tumour_prediction\frontend\public\app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Fix updateProbBar
old_prob_bar = """function updateProbBar(name, val) {
        document.getElementById(`prob-val-${name}`).textContent = `${((val||0)*100).toFixed(1)}%`;
        document.getElementById(`prob-bar-${name}`).style.width = `${((val||0)*100).toFixed(1)}%`;
    }"""
new_prob_bar = """function updateProbBar(name, val) {
        const valEl = document.getElementById(`prob-val-${name}`);
        if(valEl) valEl.textContent = `${((val||0)*100).toFixed(1)}%`;
        const barEl = document.getElementById(`prob-bar-${name}`);
        if(barEl) barEl.style.width = `${((val||0)*100).toFixed(1)}%`;
    }"""
js = js.replace(old_prob_bar, new_prob_bar)

# Fix updateModelMincard
old_model_card = """function updateModelMincard(predEl, confEl, modelData) {
        if (!modelData || modelData.class_name === 'unavailable') {
            predEl.textContent = 'N/A'; confEl.textContent = 'Not loaded'; return;
        }
        predEl.textContent = getDisplayName(modelData.class_name).toUpperCase();
        confEl.textContent = `${(modelData.confidence * 100).toFixed(1)}% confidence`;
    }"""
new_model_card = """function updateModelMincard(predEl, confEl, modelData) {
        if (!modelData || modelData.class_name === 'unavailable') {
            if(predEl) predEl.textContent = 'N/A'; 
            if(confEl) confEl.textContent = 'Not loaded'; 
            return;
        }
        if(predEl) predEl.textContent = getDisplayName(modelData.class_name).toUpperCase();
        if(confEl) confEl.textContent = `${(modelData.confidence * 100).toFixed(1)}% confidence`;
    }"""
js = js.replace(old_model_card, new_model_card)

# To be completely safe against ANY null textContent assignment in displayAnalysisResults:
# Let's wrap the assignments. 
# diagBadge.textContent = ...
js = re.sub(r'diagBadge\.textContent\s*=', r'if(diagBadge) diagBadge.textContent =', js)
js = re.sub(r'diagBadge\.className\s*=', r'if(diagBadge) diagBadge.className =', js)
js = re.sub(r'gaugeValue\.textContent\s*=', r'if(gaugeValue) gaugeValue.textContent =', js)
js = re.sub(r'statAgreement\.textContent\s*=', r'if(statAgreement) statAgreement.textContent =', js)
js = re.sub(r'statUncertainty\.textContent\s*=', r'if(statUncertainty) statUncertainty.textContent =', js)
js = re.sub(r'statCi\.textContent\s*=', r'if(statCi) statCi.textContent =', js)
js = re.sub(r'opacityPct\.textContent\s*=', r'if(opacityPct) opacityPct.textContent =', js)
js = re.sub(r'recTitle\.textContent\s*=', r'if(recTitle) recTitle.textContent =', js)
js = re.sub(r'recAction\.textContent\s*=', r'if(recAction) recAction.textContent =', js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("Safe null checks added to app.js")
