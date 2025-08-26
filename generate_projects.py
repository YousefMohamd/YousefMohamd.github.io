import os
from pathlib import Path
import datetime

# إعدادات الفولدرات
BASE_DIR = Path(__file__).parent
PROJECTS_DIR = BASE_DIR / "projects"
IMG_DIR = BASE_DIR / "img" / "projects"

sections = {
    "Concept Art": "concept-art",
    "Graphic Design": "graphic-design",
}

def make_project_file(section_label, folder, filename, index):
    # استخرج الرقم من اسم الصورة (مثلاً 12 من "12-poster.jpg")
    digits = "".join([c for c in filename if c.isdigit()])
    num = int(digits) if digits else index

    # الاسم بدون الامتداد
    title = Path(filename).stem.replace("-", " ").title()

    # مسار الصورة
    img_path = f"/img/projects/{folder}/{filename}"

    # استخدم الرقم لعكس الترتيب (الأكبر = أحدث)
    # هنحوّل الرقم إلى تاريخ افتراضي (الأكبر = أقرب لليوم)
    fake_date = datetime.date(2022,1,1) + datetime.timedelta(days=(len(os.listdir(IMG_DIR/folder))-num))
    date_str = fake_date.isoformat()

    content = f"""---
layout: layouts/project.njk
title: {title}
section: {section_label}
date: {date_str}
thumb: {img_path}
tags: [project]
---

<img src="{img_path}" alt="{title}" style="width:100%;height:auto;object-fit:contain;margin-bottom:20px;">
"""
    return content

def generate_files():
    for section_label, folder in sections.items():
        target_dir = PROJECTS_DIR
        for i, fname in enumerate(sorted(os.listdir(IMG_DIR/folder))):
            if fname.startswith("."):
                continue
            # نستخدم الترتيب بالعكس حسب الرقم في الاسم
            project_file = make_project_file(section_label, folder, fname, i)
            out_path = target_dir / f"{folder}-{Path(fname).stem}.md"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(project_file)
            print("✅ Created:", out_path)

if __name__ == "__main__":
    generate_files()

