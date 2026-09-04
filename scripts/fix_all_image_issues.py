import os
import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path('/Users/Yousef/my-portfolio')
IMG_DIR = PROJECT_ROOT / 'img'
PROJECTS_DIR = IMG_DIR / 'projects'
OPTIMIZED_PROJECTS_DIR = IMG_DIR / 'optimized' / 'projects'
ELEVENTY_CONFIG = PROJECT_ROOT / '.eleventy.js'

def synchronize_image_directories():
    if not PROJECTS_DIR.exists():
        print(f"CRITICAL ERROR: Source directory {PROJECTS_DIR} does not exist.")
        return

    OPTIMIZED_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    for root, _, files in os.walk(PROJECTS_DIR):
        relative_path = Path(root).relative_to(PROJECTS_DIR)
        destination_folder = OPTIMIZED_PROJECTS_DIR / relative_path
        destination_folder.mkdir(parents=True, exist_ok=True)
        
        for file_name in files:
            source_file = Path(root) / file_name
            destination_file = destination_folder / file_name
            
            if not destination_file.exists() or source_file.stat().st_size != destination_file.stat().st_size:
                shutil.copy2(source_file, destination_file)
                copied_count += 1

    print(f"SUCCESS: Synchronized {copied_count} assets between /img/projects/ and /img/optimized/projects/.")

def sanitize_nunjucks_templates():
    njk_files = list(PROJECT_ROOT.rglob('*.njk')) + list(PROJECT_ROOT.rglob('*.html'))
    
    for template_path in njk_files:
        if 'node_modules' in template_path.parts or '_site' in template_path.parts:
            continue
            
        with open(template_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            
        modified_content = re.sub(r'<source([^>]*?)\bdata-src=["\']([^"\']+)["\']', r'<source\1data-srcset="\2"', content)
        modified_content = re.sub(r'<source([^>]*?)\bsrc=["\']([^"\']+)["\']', r'<source\1srcset="\2"', modified_content)
        
        if modified_content != content:
            with open(template_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            print(f"SUCCESS: Applied HTML5 source element attribute compliance to {template_path.relative_to(PROJECT_ROOT)}")

def update_eleventy_configuration():
    if not ELEVENTY_CONFIG.exists():
        return
        
    with open(ELEVENTY_CONFIG, 'r', encoding='utf-8') as file:
        config_content = file.read()
        
    passthrough_target = 'eleventyConfig.addPassthroughCopy("img");'
    
    if passthrough_target not in config_content:
        updated_config = config_content.replace(
            'module.exports = function(eleventyConfig) {',
            'module.exports = function(eleventyConfig) {\n  eleventyConfig.addPassthroughCopy("img");'
        )
        with open(ELEVENTY_CONFIG, 'w', encoding='utf-8') as file:
            file.write(updated_config)
        print("SUCCESS: Forced explicit root passthrough copy for /img directory in .eleventy.js")

if __name__ == "__main__":
    synchronize_image_directories()
    sanitize_nunjucks_templates()
    update_eleventy_configuration()
