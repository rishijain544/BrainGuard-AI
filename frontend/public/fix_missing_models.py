import re

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# I will add the migration logic inside loadHistory
migration_logic = """
    function loadHistory() {
        try { 
            let arr = JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; 
            // Migration for older records
            let changed = false;
            arr = arr.map(entry => {
                if (!entry.result) return entry;
                
                // If the models object is missing, try to build it from older formats or just default to null
                if (!entry.result.models) {
                    entry.result.models = {
                        cnn: { confidence: entry.result.cnn_prediction ? entry.result.cnn_prediction.confidence : null },
                        resnet: { confidence: entry.result.resnet_prediction ? entry.result.resnet_prediction.confidence : null },
                        vit: { confidence: entry.result.vit_prediction ? entry.result.vit_prediction.confidence : null }
                    };
                    changed = true;
                }
                return entry;
            });
            if (changed) {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
            }
            return arr;
        }
        catch { return []; }
    }
"""

# Replace loadHistory
start = js.find('function loadHistory()')
if start != -1:
    end = js.find('}', js.find('catch', start)) + 1
    js = js[:start] + migration_logic.strip() + js[end:]

# Now let's fix the undefined reading in updateAnalyticsPage
# Original: cnnSum += s.result.models.cnn.confidence;
analytics_replacements = {
    'cnnSum += s.result.models.cnn.confidence;': 'if (s.result?.models?.cnn?.confidence) cnnSum += s.result.models.cnn.confidence; else cnnSum += 0;',
    'resSum += s.result.models.resnet.confidence;': 'if (s.result?.models?.resnet?.confidence) resSum += s.result.models.resnet.confidence; else resSum += 0;',
    'vitSum += s.result.models.vit.confidence;': 'if (s.result?.models?.vit?.confidence) vitSum += s.result.models.vit.confidence; else vitSum += 0;',
}

for old, new in analytics_replacements.items():
    js = js.replace(old, new)

# And in updateHistoryPage (specifically renderHistoryTable)
# Original: <td style="color: #3b82f6;">${(s.result.models.cnn.confidence * 100).toFixed(1)}%</td>
history_replacements = {
    '${(s.result.models.cnn.confidence * 100).toFixed(1)}%': '${s.result?.models?.cnn?.confidence != null ? (s.result.models.cnn.confidence * 100).toFixed(1) + "%" : "N/A"}',
    '${(s.result.models.resnet.confidence * 100).toFixed(1)}%': '${s.result?.models?.resnet?.confidence != null ? (s.result.models.resnet.confidence * 100).toFixed(1) + "%" : "N/A"}',
    '${(s.result.models.vit.confidence * 100).toFixed(1)}%': '${s.result?.models?.vit?.confidence != null ? (s.result.models.vit.confidence * 100).toFixed(1) + "%" : "N/A"}'
}

for old, new in history_replacements.items():
    js = js.replace(old, new)
    
# In export CSV
csv_replacements = {
    '${(s.result.models.cnn.confidence*100).toFixed(1)}': '${s.result?.models?.cnn?.confidence != null ? (s.result.models.cnn.confidence*100).toFixed(1) : "N/A"}',
    '${(s.result.models.resnet.confidence*100).toFixed(1)}': '${s.result?.models?.resnet?.confidence != null ? (s.result.models.resnet.confidence*100).toFixed(1) : "N/A"}',
    '${(s.result.models.vit.confidence*100).toFixed(1)}': '${s.result?.models?.vit?.confidence != null ? (s.result.models.vit.confidence*100).toFixed(1) : "N/A"}'
}

for old, new in csv_replacements.items():
    js = js.replace(old, new)

with open('d:/brain_tumour_prediction/frontend/public/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
