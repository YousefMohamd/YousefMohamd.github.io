const fs = require('fs');
const path = require('path');
console.log("=== NODE.JS PATH RESOLUTION ===");
const nodePath = path.join(process.cwd(), "img", "optimized", "projects", "concept-art");
console.log(`[Node] Target: ${nodePath}\n[Node] Exists: ${fs.existsSync(nodePath)}`);
