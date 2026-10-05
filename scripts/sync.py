import os
import re
from deep_translator import GoogleTranslator

MASTER_LANG = 'com_gridbox_en-GB'
ROOT_DIR = '.' 

def translate_text(text, target_lang):
    if not text.strip():
        return ""
    
    # Превращаем ru-RU -> ru, uk-UA -> uk и т.д.
    lang_code = target_lang.split('-')[0]
    
    try:
        translated = GoogleTranslator(source='en', target=lang_code).translate(text)
        return translated if translated else ""
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        return ""

def parse_ini(filepath):
    keys = {}
    order = []
    other_lines = []
    
    if not os.path.exists(filepath):
        return keys, order, other_lines
    
    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for line in f:
            match = re.match(r'^([A-Z0-9_-]+)\s*=\s*"(.*)"', line.strip())
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

    # 1. Sort and clean up the master (en-GB) files alphabetically by key
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
                    # Если перевод уже есть и он не пустой — оставляем его (защита ручного труда)
                    if key in target_keys and target_keys[key].strip():
                        val = target_keys[key]
                    else:
                        # Если ключ новый или пустой — переводим автоматически
                        print(f"Translating new key '{key}' into {lang_code}...")
                        val = translate_text(master_keys[key], lang_code)
                    
                    f.write(f'{key}="{val}"\n')

if __name__ == '__main__':
    sync_translations()
    print("Synchronization, sorting, and translation completed successfully!")
