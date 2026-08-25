const fs = require('fs');
const path = require('path');

module.exports = function() {
  // Target physical directory from the current file context relative path
  const showreelDir = path.join(__dirname, '..', 'img', 'showreel');
  
  // Return an empty array resiliently if the directory was deleted or missed
  if (!fs.existsSync(showreelDir)) {
    console.warn(`[WARNING] Directory ${showreelDir} does not exist. Showreel is disabled.`);
    return [];
  }

  // Retrieve raw contents inside the target folder and force alphanumeric ascending sorting
  const files = fs.readdirSync(showreelDir).sort();

  // Permitted web rendering file extension architectures (Includes image and hardware-accelerated video buffers)
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'];
  
  // Isolate system hidden chunks (e.g. Mac OS .DS_Store) and process logical mapping
  const showreelData = files.filter(file => {
    const ext = path.extname(file).toLowerCase();
    return allowedExtensions.includes(ext);
  }).map(file => {
    const ext = path.extname(file).toLowerCase();
    
    // Automatically interpret markup definition tag depending on raw asset byte payload extension 
    const type = (ext === '.mp4' || ext === '.webm') ? 'video' : 'image';
    
    return {
      type: type,
      src: `/img/showreel/${file}`
    };
  });

  return showreelData;
};
