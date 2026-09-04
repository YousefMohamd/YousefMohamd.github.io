// File: _data/concept.js
const fs = require("fs");
const path = require("path");

function extractNumber(basename) {
  const m = basename.match(/\d+/);
  return m ? parseInt(m[0], 10) : -Infinity;
}

module.exports = function () {
  // STRICT FIX: Using path.resolve to ensure absolute path resolution
  const dir = path.resolve(__dirname, "..", "img", "optimized", "projects", "concept-art");
  console.log(`[Eleventy Build] Reading Concept Art from: ${dir}`);

  if (!fs.existsSync(dir)) {
    console.error(`[Eleventy Build ERROR] Directory does not exist: ${dir}`);
    return [];
  }

  const files = fs.readdirSync(dir).filter(f => !f.startsWith(".") && !f.endsWith(".part"));
  console.log(`[Eleventy Build] Found ${files.length} optimized files in Concept Art.`);
  const groupedAssets = {};

  files.forEach(f => {
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

  return Object.keys(groupedAssets).map(baseName => {
    const data = groupedAssets[baseName];
    const assetExt = data.isVideo ? '.webm' : '.webp';
    return {
      url: `/img/optimized/projects/concept-art/${baseName}${assetExt}`,
      videoUrl: data.isVideo ? `/img/optimized/projects/concept-art/${baseName}.webm` : null,
      name: baseName,
      num: extractNumber(baseName),
      type: data.isVideo ? 'video' : 'image'
    };
  }).sort((a, b) => {
    if (b.num !== a.num) return b.num - a.num;
    return a.name.localeCompare(b.name);
  });
};
