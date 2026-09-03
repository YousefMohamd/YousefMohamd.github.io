const fs = require("fs");
const path = require("path");

function extractNumber(basename) {
  const m = basename.match(/\d+/);
  return m ? parseInt(m[0], 10) : -Infinity;
}

function isTemporaryFile(name) {
  const lower = name.toLowerCase();
  return (
    lower.startsWith(".") ||
    lower.endsWith(".tmp") ||
    lower.endsWith(".part") ||
    lower.endsWith("~") ||
    lower.includes(".tmp.") ||
    lower.includes(".part.")
  );
}

module.exports = function () {
  const dir = path.join(__dirname, "..", "img", "projects", "graphic-design");
  if (!fs.existsSync(dir)) return [];

  const exts = new Set([".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]);

  return fs
    .readdirSync(dir)
    .filter((f) => {
      const ext = path.extname(f).toLowerCase();
      return exts.has(ext) && !isTemporaryFile(f);
    })
    .map((f) => {
      const full = path.join(dir, f);
      const base = path.basename(f).toLowerCase();
      const relative = path.relative(path.join(__dirname, ".."), full).replace(/\\/g, "/");
      return {
        url: `/${relative}`,
        name: base,
        num: extractNumber(base),
      };
    })
    .sort((a, b) => {
      if (b.num !== a.num) return b.num - a.num;
      return a.name.localeCompare(b.name);
    });
};
