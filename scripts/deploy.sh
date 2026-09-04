#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "INITIATING STRICT PRE-DEPLOYMENT VERIFICATION PROTOCOL"
echo "=========================================================="

echo "[1/4] Destroying stale cache directories..."
npm run clean

echo "[2/4] Executing Python lossless compression architecture..."
python3 scripts/optimize_assets.py

echo "[3/4] Running Node.js Abstract Syntax Tree refactoring engine..."
node scripts/force-macro-refactor-final.js

echo "[4/4] Compiling Eleventy static build strictly under production environments..."
ELEVENTY_ENV=production npm run build

echo "=========================================================="
echo "BUILD SUCCESSFUL. SPINNING UP LOCAL VALIDATION SERVER"
echo "=========================================================="
echo "ACTION REQUIRED: Navigate to http://localhost:8087 in Google Chrome Incognito."
echo "Execute Lighthouse Audit. If LCP < 2.5s and CLS == 0.000, you are cleared to run:"
echo "git add . && git commit -m \"Production Build Update\" && git push origin main"
echo "=========================================================="

npx @11ty/eleventy --serve --port=8087
