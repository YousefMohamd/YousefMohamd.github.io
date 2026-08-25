import os
from PIL import Image

files_to_convert = [
    "graphic-design.jpg",
    "short-films.jpg",
    "concept-art.jpg",
    "short-film-projects.jpg"
]

source_dir = "img/projects/sections"
target_dir = "img/optimized/projects/sections"

os.makedirs(target_dir, exist_ok=True)

print("🚀 إعادة معالجة وتحويل الصور الأربعة لحل مشكلة التعتيم والشفافية...\n")

for filename in files_to_convert:
    src_path = os.path.join(source_dir, filename)
    if not os.path.exists(src_path):
        print(f"⚠️ الملف غير موجود: {src_path}")
        continue
    
    base_name = os.path.splitext(filename)[0]
    target_path = os.path.join(target_dir, f"{base_name}.webp")
    
    try:
        with Image.open(src_path) as img:
            # معالجة الشفافية لمنع تحولها إلى اللون الأسود المظلم
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGBA')
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img_to_save = background
            else:
                img_to_save = img.convert('RGB')
            
            # حفظ بصيغة WebP بجودة عالية جداً وألوان زاهية
            img_to_save.save(target_path, "WEBP", quality=95, method=6)
            print(f"✅ تم إصلاح وضبط ألوان: {filename} بنجاح!")
    except Exception as e:
        print(f"❌ خطأ أثناء معالجة {filename}: {e}")

print("\n✨ انتهت المعالجة! ستظهر الصور الآن مضيئة وواضحة تماماً.")
