const fs = require("fs");
const path = require("path");
const IMG = new Set(["jpg","jpeg","png","webp","gif","avif"]);
const VID = new Set(["mp4","webm","mov","m4v","ogg","ogv"]);
const MIME = {
  jpg:"image/jpeg", jpeg:"image/jpeg", png:"image/png", webp:"image/webp", gif:"image/gif", avif:"image/avif",
  mp4:"video/mp4", m4v:"video/mp4", webm:"video/webm",
  ogg:"video/ogg", ogv:"video/ogg",
  mov:"video/quicktime"
};
module.exports = () => {
  const dir = path.join(process.cwd(), "img", "showreel");
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(n => !n.startsWith("."))
    .map(n => {
      const ext = path.extname(n).slice(1).toLowerCase();
      const type = VID.has(ext) ? "video" : (IMG.has(ext) ? "image" : "other");
      return { name:n, type, ext, mime: MIME[ext]||"", src:`/img/showreel/${encodeURIComponent(n)}` };
    })
    .filter(x => x.type !== "other")
    .sort((a,b)=> a.name.localeCompare(b.name, undefined, {numeric:true, sensitivity:"base"}));
};
