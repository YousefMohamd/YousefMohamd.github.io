# File: generate_projects.py
import os
from pathlib import Path
import datetime
import time

# STRICT FIX: Using Path(__file__).resolve().parent for absolute pathing
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"
OPTIMIZED_DIR = BASE_DIR / "img" / "optimized" / "projects"

sections = {"Concept Art": "concept-art", "Graphic Design": "graphic-design"}

def is_file_stable(file_path, wait_time=0.5):
    """Check if a file's size remains constant over a short interval."""
    initial_size = file_path.stat().st_size
    time.sleep(wait_time)
    return initial_size == file_path.stat().st_size

def make_project_file(section_label, folder, base_name, is_video, index, total_files):
    digits = "".join([c for c in base_name if c.isdigit()])
    num = int(digits) if digits else index
    title = base_name.replace("-", " ").title()
    date_str = (datetime.date(2022, 1, 1) + datetime.timedelta(days=(total_files - num))).isoformat()

    if is_video:
        media_path = f"/img/optimized/projects/{folder}/{base_name}.webm"
        media_html = f'<video autoplay loop muted playsinline src="{media_path}" style="width:100%;height:auto;object-fit:contain;margin-bottom:20px;border-radius:8px;"></video>'
    else:
        media_path = f"/img/optimized/projects/{folder}/{base_name}.webp"
        media_html = f'<img src="{media_path}" alt="{title}" style="width:100%;height:auto;object-fit:contain;margin-bottom:20px;border-radius:8px;">'

    return f"---\nlayout: layouts/project.njk\ntitle: {title}\nsection: {section_label}\ndate: {date_str}\nthumb: {media_path}\ntags: [project]\n---\n\n{media_html}\n"

def generate_files():
    for section_label, folder in sections.items():
        folder_path = OPTIMIZED_DIR / folder
        if not folder_path.exists(): continue

        unique_assets = {}
        for fname in os.listdir(folder_path):
            if fname.startswith(".") or fname.endswith(".part"): continue
            p = folder_path / fname
            if not is_file_stable(p): continue
            base = p.stem
            if base not in unique_assets: unique_assets[base] = False
            if p.suffix.lower() in ['.webm', '.mp4']: unique_assets[base] = True

        for i, base_name in enumerate(sorted(unique_assets.keys())):
            out_path = PROJECTS_DIR / f"{folder}-{base_name}.md"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(make_project_file(section_label, folder, base_name, unique_assets[base_name], i, len(unique_assets)))

if __name__ == "__main__":
    generate_files()
