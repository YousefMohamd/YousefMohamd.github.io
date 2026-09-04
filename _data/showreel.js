const fs = require('fs');
const path = require('path');

module.exports = function() {
  const showreelDir = path.join(__dirname, '..', 'img', 'showreel');
  const videoDir = path.join(showreelDir, 'video');

  if (!fs.existsSync(showreelDir)) {
    console.warn(`[WARNING] Directory ${showreelDir} does not exist. Showreel is disabled.`);
    return [];
  }

  const videoFiles = new Set();
  if (fs.existsSync(videoDir)) {
    for (const file of fs.readdirSync(videoDir)) {
      const ext = path.extname(file).toLowerCase();
      if (ext === '.mp4' || ext === '.webm') {
        videoFiles.add(path.basename(file, ext));
      }
    }
  }

  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'];

  return fs.readdirSync(showreelDir).sort().flatMap(file => {
    if (file.startsWith('.')) return [];
    const ext = path.extname(file).toLowerCase();
    if (!allowedExtensions.includes(ext)) return [];

    const base = path.basename(file, ext);

    // إذا كانت صورة GIF و لها نسخة فيديو محولة، استخدم الفيديو بدلاً منها
    if (ext === '.gif' && videoFiles.has(base)) {
      const mp4 = path.join(showreelDir, 'video', `${base}.mp4`);
      const webm = path.join(showreelDir, 'video', `${base}.webm`);
      const src = fs.existsSync(mp4) ? `/img/showreel/video/${base}.mp4` : `/img/showreel/video/${base}.webm`;
      const mime = src.endsWith('.mp4') ? 'video/mp4' : 'video/webm';
      return [{ type: 'video', src, mime }];
    }

    if (ext === '.gif') {
      return [{ type: 'image', src: `/img/showreel/${file}` }];
    }

    if (ext === '.mp4' || ext === '.webm') {
      return [{ type: 'video', src: `/img/showreel/${file}`, mime: ext === '.mp4' ? 'video/mp4' : 'video/webm' }];
    }

    return [{ type: 'image', src: `/img/showreel/${file}` }];
  });
};
