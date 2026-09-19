import os
import re

# إعدادات الأمان ونطاق العمل
TARGET_EXTENSIONS = {'.md', '.njk', '.html'}
EXCLUDE_DIRS = {'.git', 'node_modules', '_site', 'img', '.obsidian', '.idea'}

def process_project_files():
    modified_files_count = 0
    total_replacements = 0
    
    print("🚀 بدء فحص ومعالجة مسارات الصور بذكاء...\n")
    
    for root, dirs, files in os.walk('.'):
        # استثناء المجلدات النظامية والملفات غير المرغوب فيها
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in TARGET_EXTENSIONS:
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    print(f"⚠️ تخطي الملف {file_path} بسبب خطأ في القراءة: {e}")
                    continue
                
                original_content = content
                
                # 1. تحديث مسارات HTML (src=".../img/projects/...") إلى المجلد الجديد وامتداد webp
                html_pattern = re.compile(r'(src=["\'])([^"\']*?)/img/projects/([^"\']*?)\.(jpg|jpeg|png)(["\'])', re.IGNORECASE)
                content, count1 = html_pattern.subn(r'\1\2/img/optimized/projects/\3.webp\5', content)
                
                # 2. تحديث مسارات Markdown ( .../img/projects/... )
                md_pattern = re.compile(r'(\()([^)]*?)/img/projects/([^)]*?)\.(jpg|jpeg|png)(\))', re.IGNORECASE)
                content, count2 = md_pattern.subn(r'\1\2/img/optimized/projects/\3.webp\5', content)
                
                # 3. تغطية الحالات التي يكون فيها المسار مسبقاً في optimized ولكن يحتاج لتحديث الامتداد فقط
                html_opt_pattern = re.compile(r'(src=["\'])([^"\']*?)/img/optimized/projects/([^"\']*?)\.(jpg|jpeg|png)(["\'])', re.IGNORECASE)
                content, count3 = html_opt_pattern.subn(r'\1\2/img/optimized/projects/\3.webp\5', content)
                
                md_opt_pattern = re.compile(r'(\()([^)]*?)/img/optimized/projects/([^)]*?)\.(jpg|jpeg|png)(\))', re.IGNORECASE)
                content, count4 = md_opt_pattern.subn(r'\1\2/img/optimized/projects/\3.webp\5', content)

                file_changes = count1 + count2 + count3 + count4
                
                if file_changes > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    modified_files_count += 1
                    total_replacements += file_changes
                    print(f"✅ تم التحديث: {file_path} ({file_changes} مرجع صورة)")

    # تقرير التحقق والنتائج النهائية
    print("\n" + "="*50)
    print("✨ تقرير الأتمتة والتحقق (AUTOMATION SUMMARY) ✨")
    print(f"📁 عدد الملفات المعدلة بنجاح: {modified_files_count}")
    print(f"🔄 إجمالي مسارات وصيغ الصور المحدثة: {total_replacements}")
    print("="*50)
    print("🎉 عملية التحديث تمت بأمان تام دون المساس بملفات النظام!")

if __name__ == '__main__':
    process_project_files()
