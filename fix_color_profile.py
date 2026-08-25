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

print("🚀 استخراج ملفات الألوان (ICC Profiles) ومعالجة أنظمة الألوان (CMYK/RGB)...\n")

for filename in files_to_convert:
    src_path = os.path.join(source_dir, filename)
    if not os.path.exists(src_path):
        print(f"⚠️ الملف غير موجود: {src_path}")
        continue
    
    base_name = os.path.splitext(filename)[0]
    target_path = os.path.join(target_dir, f"{base_name}.webp")
    
    try:
        with Image.open(src_path) as img:
            # استخراج ملف الألوان إن وجد في الصورة الأصلية
            icc_profile = img.info.get('icc_profile')
            
            print(f"📊 معالجة {filename} | النظام اللوني: {img.mode} | ملف الألوان متاح: {bool(icc_profile)}")
            
            # المعالجة الدقيقة لأنظمة الألوان (خصوصاً CMYK الذي يسبب الظلام في المتصفحات)
            if img.mode == 'CMYK':
                img = img.convert('RGB')
            elif img.mode == 'P':
                img = img.convert('RGBA')
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # إعدادات الحفظ بصيغة WebP مع دمج ملف الألوان الأصلي
            save_kwargs = {
                "format": "WEBP",
                "quality": 95,
                "method": 6
            }
            if icc_profile:
                save_kwargs["icc_profile"] = icc_profile
            
            img.save(target_path, **save_kwargs)
            print(f"✅ تم بنجاح: تحويل وربط ملف الألوان لـ {filename}")
            
    except Exception as e:
        print(f"❌ خطأ أثناء معالجة {filename}: {e}")

print("\n✨ انتهت العملية! تم استخراج وربط الألوان والتحويل بنجاح تام.")
