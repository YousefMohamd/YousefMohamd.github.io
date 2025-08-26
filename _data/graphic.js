const fs = require("fs");
const path = require("path");

// هترتّب حسب الرقم في اسم الملف (تنازلي)، وبعدين حسب الاسم كـ fallback
function extractNumber(basename) {
  // بيلقط أول رقم في الاسم: 001, 12, 2024 ... الخ
  const m = basename.match(/\d+/);
  return m ? parseInt(m[0], 10) : -Infinity; // اللي ملوش رقم يروح في الآخر
}

module.exports = function () {
  const dir = "img/projects/graphic-design";
  if (!fs.existsSync(dir)) return [];

  const exts = new Set([".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]);
  const files = fs
    .readdirSync(dir)
    .filter((f) => {
      const ext = path.extname(f).toLowerCase();
      return exts.has(ext) && !f.startsWith("."); // اتجنب .DS_Store
    })
    .map((f) => {
      const full = path.join(dir, f);
      const base = path.basename(f).toLowerCase();
      return {
        url: "/" + full.replace(/\\/g, "/"),
        name: base,
        num: extractNumber(base),
      };
    })
    .sort((a, b) => {
      if (b.num !== a.num) return b.num - a.num; // الأكبر رقمًا الأول
      return a.name.localeCompare(b.name); // تعادل: رتب ألفبائي
    });

  return files;
};

