import os
import re

ROOT_DIR = r"D:\SalomoneWorkspace\salomoneui"

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        
        # Replace SalomoneUI
        new_content = new_content.replace("SalomoneUI", "SalomoneUI")
        new_content = new_content.replace("salomoneui", "salomoneui")
        
        # Replace SalomoneUI variations
        new_content = new_content.replace("SalomoneUI", "SalomoneUI")
        new_content = new_content.replace("SalomoneUI", "SalomoneUI")
        new_content = new_content.replace("Salomone UI", "Salomone UI")
        new_content = new_content.replace("salomoneui", "salomoneui")
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

count = 0
for root, dirs, files in os.walk(ROOT_DIR):
    # skip node_modules, .git, .venv, dist, etc
    if any(exclude in root for exclude in ['node_modules', '.git', '.venv', 'dist', 'out', '.next', '__pycache__', 'coverage']):
        continue
        
    for file in files:
        if file.endswith(('.ts', '.tsx', '.js', '.jsx', '.json', '.html', '.md', '.py', '.bat', '.txt', '.toml')):
            filepath = os.path.join(root, file)
            if replace_in_file(filepath):
                count += 1
                
print(f"Replaced text in {count} files.")
