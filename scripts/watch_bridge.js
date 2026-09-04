const fs = require('fs');
const path = require('path');

const OPTIMIZED_DIR = path.join(__dirname, '..', 'img', 'optimized', 'projects');
const TRIGGER_FILE = path.join(__dirname, '..', '_data', 'trigger.json');

console.log(`[Watch Bridge] Monitoring directory: ${OPTIMIZED_DIR}`);

// Ensure the trigger file exists initially
if (!fs.existsSync(TRIGGER_FILE)) {
    fs.writeFileSync(TRIGGER_FILE, JSON.stringify({ updated: Date.now() }));
}

let debounceTimer = null;

function fireReload() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        const payload = JSON.stringify({ updated: Date.now() });
        fs.writeFileSync(TRIGGER_FILE, payload);
        console.log(`[Watch Bridge] Detected optimized asset shift. Fired Eleventy hot-reload trigger.`);
    }, 500); // 500ms debounce to batch multiple concurrent atomic file swaps
}

if (!fs.existsSync(OPTIMIZED_DIR)) {
    fs.mkdirSync(OPTIMIZED_DIR, { recursive: true });
}

fs.watch(OPTIMIZED_DIR, { recursive: true }, (eventType, filename) => {
    if (filename && !filename.endsWith('.part')) {
        fireReload();
    }
});
