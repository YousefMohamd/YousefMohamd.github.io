#!/bin/bash
echo "=== 1. FILESYSTEM METADATA AUDIT ==="
echo "Attempting to find optimized files (case-insensitive search):"
find . -iname "optimized" -type d -exec ls -la {} \;

echo -e "\n=== 2. SYMLINK CHECK ==="
ls -la scripts/ | grep optimize_assets.py
ls -la img/ | grep optimized
readlink -f img/optimized 2>/dev/null || echo "No symlink on img/optimized"

echo -e "\n=== 3. ASCII / CORRUPTION CHECK ==="
find img/optimized/projects -type f -exec sh -c 'echo "$1" | grep -q "[^a-zA-Z0-9._/ -]" && echo "Non-ASCII: $1"' _ {} \; 2>/dev/null || echo "No corrupt paths detected."
