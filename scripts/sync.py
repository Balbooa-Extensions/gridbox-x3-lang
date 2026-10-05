import os
import re
import urllib.request
import urllib.parse
import json

MASTER_LANG = 'com_gridbox_en-GB'
ROOT_DIR = '.' 

def translate_text(text, target_lang):
    if not text.strip():
        return ""
    
    lang_code = target_lang.split('-')[0]
    
    try:
        url = "https://api.mymemory.translated.net/get?q=" + urllib.parse.quote(text) + "&langpair=en|" + lang_code
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and 'responseData' in data and data['responseData']['translatedText']:
                translated = data['responseData']['translatedText']
                if not translated.startswith("MYMEMORY WARNING") and not translated.startswith("QUERY LENGTH"):
                    return translated
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        
    return text

def parse_ini(filepath):
    keys = {}
    order = []
    other_lines = []
    
    if not os.path.exists(filepath):
        return keys, order, other_lines
    
    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for line in f:
            match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*"(.*)"', line.strip())
            if match:
                key, val = match.groups()
                keys[key] = val
                if key not in order:
                    order.append(key)
            else:
                other_lines.append(line)
                
    return keys, order, other_lines

def sync_translations():
    master_path = os.path.join(ROOT_DIR, MASTER_LANG)
    if not os.path.exists(master_path):
        print(f"Master language folder {MASTER_LANG} not found!")
        return

    master_files = []
    for root, _, files in os.walk(master_path):
        for file in files:
            if file.endswith('.ini'):
                rel_path = os.path.relpath(os.path.join(root, file), master_path)
                master_files.append(rel_path)

    for rel_path in master_files:
        master_file_path = os.path.join(master_path, rel_path)
        master_keys, master_order, master_others = parse_ini(master_file_path)
        
        sorted_keys = sorted(master_keys.keys())
        
        with open(master_file_path, 'w', encoding='utf-8') as f:
            for line in master_others:
                f.write(line)
            for key in sorted_keys:
                f.write(f'{key}="{master_keys[key]}"\n')

    print("Master language (en-GB) files sorted alphabetically successfully.")

    for item in os.listdir(ROOT_DIR):
        lang_dir = os.path.join(ROOT_DIR, item)
        if not os.path.isdir(lang_dir) or item == MASTER_LANG or not item.startswith('com_gridbox_'):
            continue

        lang_code = item.replace('com_gridbox_', '')
        print(f"Synchronizing and translating language: {item}")
        
        for rel_path in master_files:
            target_rel_path = rel_path.replace('en-GB', lang_code)
            
            target_file_path = os.path.join(lang_dir, target_rel_path)
            master_file_path = os.path.join(master_path, rel_path)
            
            master_keys, master_order, master_others = parse_ini(master_file_path)
            target_keys, _, _ = parse_ini(target_file_path)

            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

            with open(target_file_path, 'w', encoding='utf-8') as f:
                for line in master_others:
                    f.write(line)
                
                for key in master_order:
                    if key in target_keys and target_keys[key].strip():
                        val = target_keys[key]
                    else:
                        print(f"Translating new key '{key}' into {lang_code}...")
                        val = translate_text(master_keys[key], lang_code)
                    
                    f.write(f'{key}="{val}"\n')

if __name__ == '__main__':
    sync_translations()
    print("Synchronization, sorting, and translation completed successfully!")
