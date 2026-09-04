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
  const dir = path.resolve(__dirname, "..", "img", "optimized", "projects", "graphic-design");
  if (!fs.existsSync(dir)) return [];

  const files = fs.readdirSync(dir).filter((f) => !isTemporaryFile(f));
  const groupedAssets = {};

  files.forEach((f) => {
    const ext = path.extname(f).toLowerCase();
    const baseName = path.basename(f, ext);
    const isVideo = ['.webm', '.mp4'].includes(ext);

    if (!groupedAssets[baseName]) {
      groupedAssets[baseName] = { isVideo: false, name: baseName, exts: new Set() };
    }
    groupedAssets[baseName].exts.add(ext);
    if (isVideo) {
      groupedAssets[baseName].isVideo = true;
    }
  });

  return Object.keys(groupedAssets).map((baseName) => {
    const data = groupedAssets[baseName];
    let assetExt = null;

    if (data.isVideo) {
      assetExt = '.webm';
    } else {
      if (data.exts.has('.webp')) {
        assetExt = '.webp';
      } else if (data.exts.has('.png')) {
        assetExt = '.png';
      } else if (data.exts.has('.jpg')) {
        assetExt = '.jpg';
      } else if (data.exts.has('.jpeg')) {
        assetExt = '.jpeg';
      } else {
        assetExt = '.webp';
      }
    }

    const videoUrl = data.isVideo && data.exts.has('.webm')
      ? `/img/optimized/projects/graphic-design/${baseName}.webm`
      : null;

    return {
      url: `/img/optimized/projects/graphic-design/${baseName}${assetExt}`,
      videoUrl,
      name: baseName,
      num: extractNumber(baseName),
      type: data.isVideo ? 'video' : 'image'
    };
  }).sort((a, b) => {
    if (b.num !== a.num) return b.num - a.num;
    return a.name.localeCompare(b.name);
  });
};
