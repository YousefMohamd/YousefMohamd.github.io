const fs = require('fs');
const path = require('path');

const requiredDirs = ['img/optimized', 'img/icons', 'fonts', 'css', 'js'];
let missing = 0;

console.log("🔍 Verifying Asset Directories...");

requiredDirs.forEach(dir => {
    const fullPath = path.join(__dirname, '..', dir);
    if (!fs.existsSync(fullPath)) {
        console.warn(`⚠️  [WARNING] Directory missing: ${dir}. Please make sure you have placed your assets here.`);
        missing++;
    } else {
        console.log(`✅  [OK] Directory exists: ${dir}`);
    }
});

if (missing === 0) {
    console.log("🚀 All asset directories are in place. Proceeding to build...");
} else {
    console.log("⚠️  Proceeding with build, but some assets might be missing.");
}
