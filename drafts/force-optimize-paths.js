const fs = require('fs');
const path = require('path');

function forceReplacePaths(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    
    // تخطي المجلدات غير الخاصة بالمحتوى لتسريع الفحص
    if (fs.statSync(fullPath).isDirectory()) {
      if (!['node_modules', '_site', '.git', 'img', 'css', 'js', 'fonts'].includes(file)) {
        forceReplacePaths(fullPath);
      }
    } else if (fullPath.endsWith('.md') || fullPath.endsWith('.njk') || fullPath.endsWith('.html')) {
      let content = fs.readFileSync(fullPath, 'utf8');
      
      // الفرض الجبري لتغيير المسارات والامتدادات
      let newContent = content
        .replace(/\/img\/projects\//g, '/img/optimized/projects/')
        .replace(/\.jpg/gi, '.webp')
        .replace(/\.jpeg/gi, '.webp')
        .replace(/\.png/gi, '.webp');
        
      // حفظ الملف فقط إذا تم العثور على صور ثقيلة وتعديلها
      if (content !== newContent) {
        fs.writeFileSync(fullPath, newContent, 'utf8');
        console.log(`[تم التوجيه الإجباري بنجاح] ➔ ${fullPath}`);
      }
    }
  }
}

console.log("بدء عملية الزحف لفرض مسارات الصور المُحسنة...");
forceReplacePaths(__dirname);
console.log("اكتملت العملية بنجاح! جميع المقالات تقرأ الآن من img/optimized/");
