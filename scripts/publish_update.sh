#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "STARTING INCREMENTAL UPDATE AND DEPLOY"
echo "=========================================================="

# 1. Pull latest changes from remote (if the branch exists)
git pull --rebase

# 2. Sync ghost assets (remove derived files whose source is gone)
npm run sync-assets

# 3. Optimize images/videos (idempotent – safe to run every time)
npm run optimize

# 4. Rewrite image paths in content to point to the optimized folder
npm run refactor

# 5. Build the static site, skipping the pre-build asset pipeline
#    because we already ran optimizations above
SKIP_ASSET_PIPELINE=1 ELEVENTY_ENV=production npm run build

echo "=========================================================="
echo "BUILD SUCCESSFUL"
echo "=========================================================="

# 6. Commit and push the changes automatically
#    Comment these lines if you prefer to push manually
git add .
git commit -m "Deploy update: $(date +'%Y-%m-%d %H:%M')"
git push origin main

echo "=========================================================="
echo "DEPLOYED SUCCESSFULLY TO GITHUB PAGES"
echo "=========================================================="
