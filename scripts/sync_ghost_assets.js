const fs = require('fs');
const path = require('path');

const SOURCE_DIR = path.join(__dirname, '..', 'img', 'projects');
const OPTIMIZED_DIR = path.join(__dirname, '..', 'img', 'optimized', 'projects');

// Strict Derivative Rules Mapping structurally cleanly correctly dynamically
const IMAGE_SOURCE_EXTS = ['.jpg', '.jpeg', '.png', '.webp', '.avif'];
const VIDEO_SOURCE_EXTS = ['.gif', '.mp4', '.webm', '.mov', '.ogg'];

function getSourceMap(directory) {
  let map = new Map();
  if (!fs.existsSync(directory)) return map;

  function traverse(dir) {
    fs.readdirSync(dir).forEach(file => {
      const fullPath = path.join(dir, file);
      if (fs.statSync(fullPath).isDirectory()) {
        traverse(fullPath);
      } else {
        if (!file.startsWith('.')) {
          const ext = path.extname(file).toLowerCase();
          const base = path.basename(file, ext);
          const relDir = path.relative(directory, dir);
          const key = path.join(relDir, base);

          if (!map.has(key)) map.set(key, new Set());
          map.get(key).add(ext);
        }
      }
    });
  }
  traverse(directory);
  return map;
}

console.log("=== INITIATING DERIVATIVE GHOST ASSET SYNCHRONIZATION PROTOCOL ===");

const sourceMap = getSourceMap(SOURCE_DIR);
let deletedCount = 0;

if (fs.existsSync(OPTIMIZED_DIR)) {
  function cleanOptimized(dir) {
    fs.readdirSync(dir).forEach(file => {
      const fullPath = path.join(dir, file);
      if (fs.statSync(fullPath).isDirectory()) {
        cleanOptimized(fullPath);
      } else {
        if (!file.startsWith('.')) {
          const ext = path.extname(file).toLowerCase();
          const base = path.basename(file, ext);
          const relDir = path.relative(OPTIMIZED_DIR, dir);
          const checkKey = path.join(relDir, base);

          const sourceExts = sourceMap.get(checkKey);
          let shouldDelete = false;

          // 1. If base file name doesn't exist in source AT ALL
          if (!sourceExts) {
            shouldDelete = true;
          }
          // 2. If Optimized is WebP/AVIF, source MUST have a static image extension
          else if (['.webp', '.avif'].includes(ext)) {
            const hasImageSource = Array.from(sourceExts).some(e => IMAGE_SOURCE_EXTS.includes(e));
            if (!hasImageSource) shouldDelete = true;
          }
          // 3. If Optimized is WebM/MP4, source MUST have a video/gif extension
          else if (['.webm', '.mp4'].includes(ext)) {
            const hasVideoSource = Array.from(sourceExts).some(e => VIDEO_SOURCE_EXTS.includes(e));
            if (!hasVideoSource) shouldDelete = true;
          }

          // Execute Surgical Deletion
          if (shouldDelete) {
            fs.unlinkSync(fullPath);
            deletedCount++;
            console.log(`[PURGED DERIVATIVE GHOST ASSET]: ${fullPath}`);
          }
        }
      }
    });
  }
  cleanOptimized(OPTIMIZED_DIR);
}

console.log(`=== COMPLETED GHOST ASSET SYNCHRONIZATION: ${deletedCount} DERIVATIVE GHOSTS PURGED ===\n`);
