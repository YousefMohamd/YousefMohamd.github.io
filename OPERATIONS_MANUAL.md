# ARCHITECTURAL OPERATIONS & MAINTENANCE MANUAL
## SYSTEM CONTEXT
This document serves as the absolute operational runbook for the Yousef Mohamed Portfolio repository. It defines the exact execution commands required for local development, production deployment, and system maintenance.

## 1. LOCAL DEVELOPMENT & ACTIVE CODING
Use this command during standard HTML/CSS/JS editing.
- Execution Command: `npm run serve`
- System Action: Initializes the Eleventy local development server with active hot-reloading. Bypasses heavy image compression for speed.

## 2. PRODUCTION BUILD EXECUTION
Use this command to force a complete, optimized system compilation without deploying.
- Execution Command: `npm run prod:build`
- System Action: 
  1. Purges the `_site` directory.
  2. Executes the Python asset optimization pipeline (`optimize_assets.py`).
  3. Executes Node.js macro refactoring.
  4. Compiles the Eleventy environment strictly under `ELEVENTY_ENV=production`.

## 3. SECURE DEPLOYMENT PROTOCOL (PRE-FLIGHT CHECK)
Use this command strictly before pushing any code to the GitHub repository.
- Execution Command: `npm run deploy`
- System Action: Executes the entire `prod:build` pipeline and subsequently spins up an isolated staging server on `http://localhost:8087`.
- Validation Requirement: You must open an Incognito window, verify visual integrity, and confirm Lighthouse performance metrics before executing standard git commit and push commands.

## 4. LONG-TERM SYSTEM MAINTENANCE (COLD-FLUSH)
Use this command monthly or after deleting multiple legacy images from the source directory.
- Execution Command: `npm run maintenance`
- System Action: 
  1. Audits Node.js vulnerabilities.
  2. Upgrades core Python imaging algorithms (Pillow, pillow-heif).
  3. Executes a Cold-Storage Flush: Deletes all processed binary assets in `img/optimized/projects/` and forces a complete regeneration from the source directory to permanently erase orphaned files.

## 5. CACHE INVALIDATION (CDN EDGE PURGE)
Use this manual procedure if layout changes do not appear on live mobile devices.
- Target File: `_includes/layouts/base.njk`
- Manual Action: Locate the stylesheet link tags. Increment the query string integer (e.g., change `?v=systemOverride4` to `?v=systemOverride5`).
- System Action: Forces global Content Delivery Networks (GitHub Pages / Fastly) to purge the cached stylesheet and serve the new structural parameters instantly.
