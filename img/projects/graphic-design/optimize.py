import os
from PIL import Image

def quick_optimize():
    filename = input("17").strip()
    base_name = filename.split('.')[0]

    found_file = None
    for ext in ['jpg','jpeg','png','JPG','PNG']:
        f = f"{base_name}.{ext}"
        if os.path.exists(f):
            found_file = f
            break

    if not found_file:
        print("❌ الملف غير موجود")
        return

    original_size = os.path.getsize(found_file)
    img = Image.open(found_file).convert("RGB")
    out = f"optimized_{found_file}"
    img.save(out, optimize=True, quality=80)
    new_size = os.path.getsize(out)

    print(f"✅ {original_size//1024}KB → {new_size//1024}KB")

quick_optimize()
