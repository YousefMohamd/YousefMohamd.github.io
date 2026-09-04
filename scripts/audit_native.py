import os
import re
from pathlib import Path

SITE_DIR = Path('/Users/Yousef/my-portfolio/_site')
SIZE_LIMIT_KB = 300

def run_strict_audit():
    if not SITE_DIR.exists():
        print("CRITICAL ERROR: The _site directory does not exist. Execute the Eleventy build command before running this audit.")
        return

    missing_files_registry = set()
    heavy_files_registry = []

    url_extraction_pattern = re.compile(r'(?:src|srcset|data-src|data-srcset)=["\']([^"\']+)["\']')

    for html_file_path in SITE_DIR.rglob('*.html'):
        with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as current_file:
            file_content = current_file.read()
            extracted_urls = url_extraction_pattern.findall(file_content)
            for raw_url in extracted_urls:
                clean_url = raw_url.split(',')[0].strip().split(' ')[0].split('?')[0]
                
                if clean_url.startswith('/') and not clean_url.startswith('//'):
                    local_system_path = SITE_DIR / clean_url.lstrip('/')
                    
                    if not local_system_path.exists():
                        missing_files_registry.add(clean_url)
                    else:
                        file_size_in_kb = local_system_path.stat().st_size / 1024
                        if file_size_in_kb > SIZE_LIMIT_KB:
                            heavy_files_registry.append((clean_url, file_size_in_kb))

    print("\n--- CRITICAL 404 MISSING ASSETS REGISTRY ---")
    for missing_asset in sorted(missing_files_registry):
        print(f"ASSET NOT FOUND: {missing_asset}")

    print("\n--- HEAVY ASSETS REGISTRY (EXCEEDING 300KB) ---")
    for heavy_asset, asset_size in sorted(heavy_files_registry, key=lambda item: item[1], reverse=True):
        print(f"HEAVY ASSET DETECTED: {heavy_asset} ({asset_size:.1f} KB)")

if __name__ == "__main__":
    run_strict_audit()
