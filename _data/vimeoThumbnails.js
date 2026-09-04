const fs = require('fs');
const path = require('path');

function extractVimeoId(content) {
  const match = content.match(/vimeoId:\s*(\d+)/);
  return match ? match[1] : null;
}

async function fetchVimeoThumbnail(id) {
  try {
    const url = `https://vimeo.com/api/oembed.json?url=https://vimeo.com/${id}`;
    const response = await fetch(url);
    const data = await response.json();
    if (data.thumbnail_url) {
      const thumb = data.thumbnail_url;
      const dimensionRegex = /\d+x\d+(?=\.\w+$)/;
      let small = thumb;
      let medium = thumb;
      let large = thumb;

      if (dimensionRegex.test(thumb)) {
        small = thumb.replace(dimensionRegex, '640x360');
        medium = thumb.replace(dimensionRegex, '1280x720');
        large = thumb.replace(dimensionRegex, '1920x1080');
      }

      return {
        fallback: thumb,
        srcset: `${small} 640w, ${medium} 1280w, ${large} 1920w`
      };
    }
  } catch (err) {
    console.error(`Error fetching Vimeo thumbnail for ${id}:`, err.message);
  }
  return null;
}

module.exports = async function () {
  const dir = path.join(__dirname, '..', 'projects');
  const files = fs.readdirSync(dir).filter(f => f.startsWith('short-film-') && f.endsWith('.md'));
  const map = {};

  await Promise.all(files.map(async (file) => {
    const content = fs.readFileSync(path.join(dir, file), 'utf8');
    const id = extractVimeoId(content);
    if (!id) return;
    const data = await fetchVimeoThumbnail(id);
    if (data) {
      map[id] = data;
    }
  }));

  return map;
};
