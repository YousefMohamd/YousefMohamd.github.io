import os
from PIL import Image, ImageEnhance

files_to_convert = [
    "graphic-design.jpg",
    "short-films.jpg",
    "concept-art.jpg",
    "short-film-projects.jpg"
]

source_dir = "img/projects/sections"
target_dir = "img/optimized/projects/sections"

os.makedirs(target_dir, exist_ok=True)

print("🚀 تفتيح وتحسين إضاءة وتباين صور الأقسام...\n")

for filename in files_to_convert:
    src_path = os.path.join(source_dir, filename)
    if not os.path.exists(src_path):
        print(f"⚠️ الملف غير موجود: {src_path}")
        continue
    
    base_name = os.path.splitext(filename)[0]
    target_path = os.path.join(target_dir, f"{base_name}.webp")
    
    try:
        with Image.open(src_path) as img:
            img = img.convert('RGB')
            
            # زيادة الإضاءة بنسبة 40% للتخلص من العتمة والظلام
            enhancer_bright = ImageEnhance.Brightness(img)
            img = enhancer_bright.enhance(1.4)
            
            # زيادة التباين بنسبة 20% لتبرز تفاصيل الصورة بوضوح
            enhancer_contrast = ImageEnhance.Contrast(img)
            img = enhancer_contrast.enhance(1.2)
            
            # حفظ بصيغة WebP بجودة ممتازة
            img.save(target_path, "WEBP", quality=95, method=6)
            print(f"✅ تم تفتيح وتحسين صورة: {filename}")
    except Exception as e:
        print(f"❌ خطأ أثناء معالجة {filename}: {e}")

print("\n✨ تمت العملية بنجاح! جرب تحديث صفحة الموقع الآن لتريها مضيئة وواضحة.")
