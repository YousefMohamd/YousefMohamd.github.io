#!/usr/bin/env bash

REPORT_FILE="diagnostic_report.txt"
> "$REPORT_FILE"

echo "================ ARCHITECTURE DIAGNOSTIC REPORT ================" | tee -a "$REPORT_FILE"

echo "[1] ASSET PHYSICAL PATHS (Top 20 Source & Output Files):" | tee -a "$REPORT_FILE"
find ./img ./_site/img -type f \( -name "*.webp" -o -name "*.avif" -o -name "*.jpg" \) 2>/dev/null | head -n 20 | tee -a "$REPORT_FILE"

echo -e "\n[2] ELEVENTY PASSTHROUGH CONFIGURATION (.eleventy.js):" | tee -a "$REPORT_FILE"
grep -n "addPassthroughCopy" .eleventy.js 2>/dev/null | tee -a "$REPORT_FILE"

echo -e "\n[3] FAULTY TEMPLATE SYNTAX (<picture> / <source> in .njk):" | tee -a "$REPORT_FILE"
grep -rnE "<source|<picture" . --include=\*.njk --exclude-dir=node_modules --exclude-dir=_site | tee -a "$REPORT_FILE"

echo -e "\n[4] DATA STRUCTURE (JSON image fields):" | tee -a "$REPORT_FILE"
grep -rnE "\"image" . --include=\*.json --exclude-dir=node_modules --exclude-dir=_site | head -n 15 | tee -a "$REPORT_FILE"

echo "================================================================" | tee -a "$REPORT_FILE"
