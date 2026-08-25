import os
from PIL import Image

# الملفات الأربعة المحددة بدقة
files_to_convert = [
    "graphic-design.jpg",
    "short-films.jpg",
    "concept-art.jpg",
    "short-film-projects.jpg"
]

source_dir = "img/projects/sections"
target_dir = "img/optimized/projects/sections"

# التأكد من وجود مجلد الإخراج
os.makedirs(target_dir, exist_ok=True)

print("🚀 بدء تحويل الصور الأربعة إلى WebP بجودة عالية وحفاظ تام على الألوان...\n")

for filename in files_to_convert:
    src_path = os.path.join(source_dir, filename)
    if not os.path.exists(src_path):
        print(f"⚠️ الملف غير موجود: {src_path}")
        continue
    
    base_name = os.path.splitext(filename)[0]
    target_path = os.path.join(target_dir, f"{base_name}.webp")
    
    try:
        with Image.open(src_path) as img:
            # ضمان تحويل الصورة لنمط RGB لسلامة الألوان وعدم حدوث تداخل
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")
            
            # حفظ بصيغة WebP بجودة ممتازة (92) مع أعلى دقة ضغط (method=6)
            img.save(target_path, "WEBP", quality=92, method=6)
            print(f"✅ تم تحويل وحفظ: {filename} -> {target_path}")
    except Exception as e:
        print(f"❌ خطأ أثناء معالجة {filename}: {e}")

print("\n✨ انتهت عملية تحويل صور الأقسام بنجاح تام وبأعلى جودة!")
