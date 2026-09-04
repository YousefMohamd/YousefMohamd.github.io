import os
from pathlib import Path

PROJECT_ROOT = Path('/Users/Yousef/my-portfolio')
OUTPUT_REPORT = PROJECT_ROOT / 'scripts' / 'project_architecture_dump.txt'

def dump_project_state():
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as report:
        
        report.write("=== ELEVENTY CONFIGURATION (.eleventy.js) ===\n")
        config_file = PROJECT_ROOT / '.eleventy.js'
        if config_file.exists():
            report.write(config_file.read_text(encoding='utf-8'))
        else:
            report.write("Configuration file not found.\n")
        report.write("\n" + "="*50 + "\n\n")

        report.write("=== ASSET INVENTORY (img/ directory hierarchy) ===\n")
        img_dir = PROJECT_ROOT / 'img'
        if img_dir.exists():
            for path in sorted(img_dir.rglob('*')):
                if path.is_file():
                    relative_path = path.relative_to(PROJECT_ROOT)
                    file_size_kb = path.stat().st_size / 1024
                    report.write(f"{relative_path} [{file_size_kb:.1f} KB]\n")
        report.write("\n" + "="*50 + "\n\n")

        report.write("=== TEMPLATE STRUCTURES (.njk files) ===\n")
        for njk_path in sorted(PROJECT_ROOT.rglob('*.njk')):
            if 'node_modules' in njk_path.parts or '_site' in njk_path.parts:
                continue
            report.write(f"--- FILE PATH: {njk_path.relative_to(PROJECT_ROOT)} ---\n")
            report.write(njk_path.read_text(encoding='utf-8'))
            report.write("\n" + "-"*30 + "\n\n")

        report.write("=== DATA STRUCTURES (.json files) ===\n")
        for json_path in sorted(PROJECT_ROOT.rglob('*.json')):
            if 'node_modules' in json_path.parts or '_site' in json_path.parts:
                continue
            report.write(f"--- FILE PATH: {json_path.relative_to(PROJECT_ROOT)} ---\n")
            report.write(json_path.read_text(encoding='utf-8'))
            report.write("\n" + "-"*30 + "\n\n")

    print(f"SUCCESS: Complete project architecture payload compiled strictly at {OUTPUT_REPORT}")

if __name__ == '__main__':
    dump_project_state()
