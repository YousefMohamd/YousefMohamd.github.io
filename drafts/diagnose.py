import os
import subprocess

print("="*60)
print("🔍 تقرير التشخيص الشامل لأداء وصور الموقع")
print("="*60)

# 1. حالة الـ Git
print("\n[1] حالة الـ Git الحالية:")
try:
    res = subprocess.run(['git', 'status', '-s'], capture_output=True, text=True)
    if res.stdout.strip():
        print(res.stdout)
    else:
        print("✅ المجلد نظيف ولا توجد تعديلات معلقة غير محفوظة.")
except Exception as e:
    print(f"خطأ في فحص Git: {e}")

# 2. فحص الروابط القديمة المتبقية في ملفات المحتوى
print("\n[2] فحص الروابط القديمة (/img/projects/):")
old_refs_count = 0
target_extensions = {'.md', '.njk', '.html'}
exclude_dirs = {'.git', 'node_modules', '_site', '.obsidian', '.idea'}

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if os.path.splitext(file)[1].lower() in target_extensions:
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '/img/projects/' in content:
                        old_refs_count += 1
                        print(f"⚠️ وجد مسار قديم في: {path}")
            except:
                pass

if old_refs_count == 0:
    print("✅ ممتاز جداً! لا توجد أي روابط قديمة لـ /img/projects/ في ملفات المحتوى.")
else:
    print(f"❌ تحذير: وُجدت روابط قديمة في {old_refs_count} ملف.")

# 3. فحص أحجام الصور المحسنة للتأكد من عدم وجود صور ضخمة
print("\n[3] فحص أحجام الصور داخل مجلد optimized (بحث عن صور > 500 كيلوبايت):")
opt_dir = 'img/optimized/projects'
large_images = []
total_images = 0

if os.path.exists(opt_dir):
    for root, dirs, files in os.walk(opt_dir):
        for file in files:
            if file.endswith(('.webp', '.avif')):
                total_images += 1
                fpath = os.path.join(root, file)
                size_kb = os.path.getsize(fpath) / 1024
                if size_kb > 500:
                    large_images.append((fpath, size_kb))
    
    print(f"📊 إجمالي الصور المحسنة المفحوصة: {total_images} صورة.")
    if large_images:
        print("⚠️ تم العثور على صور ضخمة قد تسبب البطء:")
        for img, sz in large_images:
            print(f"   - {img} ({sz:.1f} KB)")
    else:
        print("✅ جميع أحجام الصور المحسنة ممتازة وصغيرة (أقل من 500KB).")
else:
    print("❌ عذراً، مجلد img/optimized/projects غير موجود محلياً!")

print("\n" + "="*60)
print("🏁 انتهى تقرير التشخيص. انسخ هذه النتيجة وأرسلها لي فوراً!")
print("="*60)
