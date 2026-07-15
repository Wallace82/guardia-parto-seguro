import os
import re

directories = ['guardia-frontend', 'docs']
extensions = ['.ts', '.html', '.md']

for directory in directories:
    for root, _, files in os.walk(directory):
        if 'node_modules' in root or '.angular' in root:
            continue
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    # 1. Replace the full phrase
                    new_content = re.sub(r'(?i)Índice de Risco Assistencial', 'Índice GuardIA de Atenção', new_content)
                    
                    # 2. Replace the acronym
                    new_content = re.sub(r'\bIRA\b', 'IGA', new_content)
                    
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated {filepath}")
                except Exception as e:
                    print(f"Failed to process {filepath}: {e}")

print("Done replacing.")
