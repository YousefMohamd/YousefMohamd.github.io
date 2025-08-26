const fs = require("fs");
const path = require("path");

function extractNumber(basename) {
  const m = basename.match(/\d+/);
  return m ? parseInt(m[0], 10) : -Infinity;
}

module.exports = function () {
  const dir = "img/projects/concept-art";
  if (!fs.existsSync(dir)) return [];

  const exts = new Set([".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]);
  const files = fs
    .readdirSync(dir)
    .filter((f) => {
      const ext = path.extname(f).toLowerCase();
      return exts.has(ext) && !f.startsWith(".");
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
      if (b.num !== a.num) return b.num - a.num;
      return a.name.localeCompare(b.name);
    });

  return files;
};

