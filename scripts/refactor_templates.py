import os
import re
from pathlib import Path

ROOT_DIR = Path('/Users/Yousef/my-portfolio')

def apply_strict_refactoring():
    target_files = list(ROOT_DIR.rglob('*.njk'))
    
    anomaly_patterns = [
        r'<source[^>]*src=["\']\{\{\s*([a-zA-Z0-9_\.]+)(?:\s*\|\s*url)?\s*\}\}["\'][^>]*>',
        r'<source[^>]*srcset=["\']\{\{\s*([a-zA-Z0-9_\.]+)(?:\s*\|\s*url)?\s*\}\}["\'][^>]*>',
        r'<source[^>]*data-src=["\']\{\{\s*([a-zA-Z0-9_\.]+)(?:\s*\|\s*url)?\s*\}\}["\'][^>]*>',
        r'<source[^>]*data-srcset=["\']\{\{\s*([a-zA-Z0-9_\.]+)(?:\s*\|\s*url)?\s*\}\}["\'][^>]*>'
    ]

    for njk_path in target_files:
        if 'node_modules' in njk_path.parts or '_site' in njk_path.parts:
            continue

        with open(njk_path, 'r', encoding='utf-8') as file:
            content = file.read()

        modified = False
        for pattern in anomaly_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                full_match = match.group(0)
                variable_name = match.group(1)
                
                strict_nunjucks_block = (
                    f'{{% set base_path = {variable_name} | replace(".jpg", "") | replace(".jpeg", "") | replace(".png", "") %}}\n'
                    f'            <source type="image/avif" data-srcset="{{{{ (base_path ~ \'.avif\') | url }}}}">\n'
                    f'            <source type="image/webp" data-srcset="{{{{ (base_path ~ \'.webp\') | url }}}}"'
                )
                
                if full_match in content:
                    content = content.replace(full_match, strict_nunjucks_block + '>')
                    modified = True

        if modified:
            with open(njk_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"SUCCESS: Architectural refactoring applied strictly to {njk_path.name}")

if __name__ == "__main__":
    apply_strict_refactoring()
