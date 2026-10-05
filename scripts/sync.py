import os
import re

MASTER_LANG = 'com_gridbox_en-GB'
ROOT_DIR = '.' 

def parse_ini(filepath):
    """
    Parses a Joomla INI file.
    Returns:
        keys (dict): Dictionary of key-value pairs.
        order (list): List of keys in the exact order they appeared.
        comments (dict): Stores comments or other non-key lines mapped to their position.
    """
    keys = {}
    order = []
    other_lines = []
    
    if not os.path.exists(filepath):
        return keys, order, other_lines
    
    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for line in f:
            # Look for lines in the format KEY="Value"
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

    # Collect all .ini files from the master folder
    master_files = []
    for root, _, files in os.walk(master_path):
        for file in files:
            if file.endswith('.ini'):
                rel_path = os.path.relpath(os.path.join(root, file), master_path)
                master_files.append(rel_path)

    # 1. First, sort and clean up the master (en-GB) files alphabetically by key
    for rel_path in master_files:
        master_file_path = os.path.join(master_path, rel_path)
        master_keys, master_order, master_others = parse_ini(master_file_path)
        
        # Sort master keys alphabetically
        sorted_keys = sorted(master_keys.keys())
        
        with open(master_file_path, 'w', encoding='utf-8') as f:
            # Write header comments if any exist at the top
            for line in master_others:
                f.write(line)
            # Write sorted keys
            for key in sorted_keys:
                f.write(f'{key}="{master_keys[key]}"\n')

    print("Master language (en-GB) files sorted alphabetically successfully.")

    for item in os.listdir(ROOT_DIR):
        lang_dir = os.path.join(ROOT_DIR, item)
        if not os.path.isdir(lang_dir) or item == MASTER_LANG or not item.startswith('com_gridbox_'):
            continue

        lang_code = item.replace('com_gridbox_', '')
        print(f"Synchronizing language: {item}")
        
        for rel_path in master_files:
            target_rel_path = rel_path.replace('en-GB', lang_code)
            
            target_file_path = os.path.join(lang_dir, target_rel_path)
            master_file_path = os.path.join(master_path, rel_path)
            
            # Read fresh master data (already sorted)
            master_keys, master_order, master_others = parse_ini(master_file_path)
            target_keys, _, _ = parse_ini(target_file_path)

            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

            # Write the target file matching the master's structure and sorted order
            with open(target_file_path, 'w', encoding='utf-8') as f:
                for line in master_others:
                    f.write(line)
                
                for key in master_order:
                    # Keep existing translation if present, otherwise fallback to master value
                    val = target_keys.get(key, master_keys[key])
                    f.write(f'{key}="{val}"\n')

if __name__ == '__main__':
    sync_translations()
    print("Synchronization and sorting completed successfully!")
