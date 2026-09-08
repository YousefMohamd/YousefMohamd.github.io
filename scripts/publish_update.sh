set -e

git pull --rebase

npm run sync-assets

npm run optimize

npm run refactor

SKIP_ASSET_PIPELINE=1 ELEVENTY_ENV=production npm run build

git add .
git commit -m "Deploy update: $(date +'%Y-%m-%d %H:%M')"
git push origin main
