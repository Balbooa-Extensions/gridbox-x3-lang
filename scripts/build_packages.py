import os
import zipfile
from datetime import datetime

ROOT_DIR = '.'
RELEASE_DIR = 'releases'

def build_zip_packages():
    if not os.path.exists(RELEASE_DIR):
        os.makedirs(RELEASE_DIR)

    # Get current date automatically in format like "05 October 2026" or "03 July 2026"
    current_date = datetime.utcnow().strftime('%d %B %Y')

    # Iterate through all language folders
    for item in os.listdir(ROOT_DIR):
        lang_dir = os.path.join(ROOT_DIR, item)
        if not os.path.isdir(lang_dir) or item == 'com_gridbox_en-GB' or not item.startswith('com_gridbox_'):
            continue

        lang_code = item.replace('com_gridbox_', '')
        print(f"Building package for: {lang_code}")

        # Path to template
        template_path = os.path.join(lang_dir, 'install.xml.template')
        if not os.path.exists(template_path):
            print(f"Warning: install.xml.template not found in {item}, skipping.")
            continue

        # Generate install.xml from template (replacing language code and current date)
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        install_xml_content = template_content.replace('{LANG_CODE}', lang_code)
        install_xml_content = install_xml_content.replace('{CURRENT_DATE}', current_date)
        
        install_xml_path = os.path.join(lang_dir, 'install.xml')
        with open(install_xml_path, 'w', encoding='utf-8') as f:
            f.write(install_xml_content)

        # Create ZIP archive
        zip_filename = f"com_gridbox_{lang_code}.zip"
        zip_path = os.path.join(RELEASE_DIR, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add generated install.xml at the root of the ZIP
            zipf.write(install_xml_path, 'install.xml')

            # Add administrator files
            admin_folder = os.path.join(lang_dir, 'administrator')
            if os.path.exists(admin_folder):
                for root, _, files in os.walk(admin_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join('administrator', os.path.relpath(file_path, admin_folder))
                        zipf.write(file_path, arcname)

            # Add site files
            site_folder = os.path.join(lang_dir, 'site')
            if os.path.exists(site_folder):
                for root, _, files in os.walk(site_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join('site', os.path.relpath(file_path, site_folder))
                        zipf.write(file_path, arcname)

        # Clean up temporary install.xml from source directory
        if os.path.exists(install_xml_path):
            os.remove(install_xml_path)

        print(f"Created: {zip_path}")

if __name__ == '__main__':
    build_zip_packages()
    print("All language packages built successfully!")
