import os
from pathlib import Path
from bs4 import BeautifulSoup

SITE_DIR = Path('_site')
SIZE_LIMIT_KB = 300 # تنبيه لأي صورة تتجاوز 300 كيلوبايت

def run_audit():
    if not SITE_DIR.exists():
        print(f"ERROR: {SITE_DIR} not found. Run Eleventy build first.")
        return

    missing_assets = set()
    heavy_assets = []

    for html_file in SITE_DIR.rglob('*.html'):
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Check img src and source srcset
            for tag in soup.find_all(['img', 'source']):
                asset_path = tag.get('src') or tag.get('srcset')
                if asset_path and asset_path.startswith('/'):
                    # Convert absolute web path to local path
                    local_path = SITE_DIR / asset_path.lstrip('/')
                    
                    if not local_path.exists():
                        missing_assets.add(asset_path)
                    elif local_path.stat().st_size > (SIZE_LIMIT_KB * 1024):
                        heavy_assets.append((asset_path, local_path.stat().st_size / 1024))

    print("\n--- 🚨 MISSING ASSETS (404 ERRORS) ---")
    for missing in missing_assets:
        print(f"NOT FOUND: {missing}")

    print("\n--- ⚠️ HEAVY ASSETS (PERFORMANCE BOTTLENECK) ---")
    for asset, size in heavy_assets:
        print(f"LARGE FILE: {asset} ({size:.1f} KB)")

if __name__ == "__main__":
    # pip install beautifulsoup4
    run_audit()
