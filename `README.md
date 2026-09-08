# Dark-Portfolio-Template-11ty

A starter repository showing how to build a blog with the [Eleventy](https://github.com/11ty/eleventy) static site generator.
Uses the W3CSS template "Dark Portfolio Template"

[![Build Status](https://travis-ci.com/jmschrack/Dark-Portfolio-Template-11ty.svg?branch=dev)](https://travis-ci.org/jmschrack/dark-portfolio-template-11ty)

## Demos

* [GitHub Pages](https://jmschrack.github.io/Dark-Portfolio-Template-11ty/)

## Getting Started

### 1. Clone this Repository

```
git clone https://github.com/jmschrack/Dark-Portfolio-Template-11ty.git my-blog-name
```

### 2. Navigate to the directory

```
cd my-blog-name
```

Specifically have a look at `.eleventy.js` to see if you want to configure any Eleventy options differently.

### 3. Install dependencies

```
npm install
```

### 4. Edit _data/metadata.json

### 5. Run Eleventy

```
npx eleventy
```

Or build and host locally for local development
```
npx eleventy --serve
```

Or build automatically when a template changes:
```
npx eleventy --watch
```

Or in debug mode:
```
DEBUG=* npx eleventy
```

## Asset Pipeline & Scripts

The project uses several custom scripts to handle images, showreel videos, and content verification.

| Script | Purpose |
|--------|---------|
| `scripts/optimize_assets.py` | Convert raster images to WebP/AVIF, transcode videos to WebM, and prune orphaned outputs. |
| `scripts/fetch_vimeo_thumbs.py` | Generate small `.webp` thumbnail previews for short-film projects using Vimeo oEmbed. |
| `scripts/sync_ghost_assets.js` | Remove derived assets (WebP/WebM) whose source files no longer exist. |
| `force-optimize-paths.js` | Rewrite image paths inside `.md`, `.njk`, and `.html` files from `/img/projects/…` to `/img/optimized/projects/…`. |
| `update_images.py` | Smart, safe version of the above script, only touching `src="…"` and markdown link syntax. |
| `audit_site.py` | After building, check all `/`-rooted assets in `_site` for missing files and files > 300 KB. |
| `audit-projects.js` | Scan markdown files for short-film entries and display their frontmatter fields. |
| `scripts/verify-assets.js` | Ensure critical folders (`img/optimized`, `img/icons`, `fonts`, `css`, `js`) exist before building. |

## Build commands

The project supports several build workflows:

- `npm run build` – Plain Eleventy build (no asset pipeline, unless invoked via `beforeBuild`).
- `npm run prod:build` – Full production build: clean, sync assets, optimize, refactor, then build with `SKIP_ASSET_PIPELINE=1`.
- `npm run prod:build:safe` – Same as above but without the refactor step.
- `npm run deploy` – Runs the deployment script (`scripts/deploy.sh`) which builds and starts a local validation server.

## Environment variable

`SKIP_ASSET_PIPELINE=1` prevents `.eleventy.js` from running the optimizer and Vimeo thumbnail fetcher during the build. Use it when you’ve already run `npm run optimize` and `npm run sync-assets` manually.

## Dependencies

- Python 3 with `Pillow`, `pillow-heif`, and `BeautifulSoup` installed.
- `ffmpeg` and `ffprobe` available in `PATH` (used for video transcoding).
- Node.js with npm dependencies installed via `npm install`.
