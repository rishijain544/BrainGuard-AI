with open('d:/brain_tumour_prediction/frontend/public/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'id="file-input"' in line or "id='file-input'" in line:
        print(f"Line {i+1}: {line.strip()}")
