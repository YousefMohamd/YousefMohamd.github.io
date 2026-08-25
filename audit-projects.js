const fs = require('fs');
const path = require('path');

function scanDir(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!['node_modules', '_site', '.git', '.eleventy'].includes(entry.name)) {
        scanDir(fullPath);
      }
    } else if (entry.name.endsWith('.md')) {
      const content = fs.readFileSync(fullPath, 'utf8');
      const match = content.match(/^---\s*([\s\S]*?)\s*---/);
      if (match) {
        const frontmatter = match[1];
        const lines = frontmatter.split('\n');
        let data = {};
        lines.forEach(line => {
          const parts = line.split(':');
          if (parts.length >= 2) {
            const key = parts[0].trim();
            const val = parts.slice(1).join(':').trim().replace(/^["']|["']$/g, '');
            data[key] = val;
          }
        });

        // نعرض فقط المشاريع التي تخص الأفلام القصيرة أو التي تحتوي على vimeoId
        if (data.vimeoId || (data.section && data.section.toLowerCase().includes('short film'))) {
          console.log(`--------------------------------------------------`);
          console.log(`📁 مسار الملف: ${fullPath}`);
          console.log(`🎬 العنوان: ${data.title || 'غير محدد'}`);
          console.log(`📂 القسم: ${data.section || 'غير محدد'}`);
          console.log(`🆔 معرف Vimeo: ${data.vimeoId || 'غير موجود'}`);
          console.log(`🖼️ بوستر مخصص: ${data.poster || 'لم يتم تعيينه بعد'}`);
        }
      }
    }
  }
}

console.log("=== بدء عملية مسح مشاريع الأفلام القصيرة ===");
scanDir('.');
console.log("==================================================");
console.log("انتهى الفحص بنجاح!");
