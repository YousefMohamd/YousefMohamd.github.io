#!/bin/bash
echo "=== DEPENDENCY AUDIT ==="
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"
echo "Eleventy version: $(npx @11ty/eleventy --version 2>/dev/null || echo 'Not found locally')"
echo "Python version: $(python3 --version)"
python3 -c "import PIL; print(f'Pillow version: {PIL.__version__}')" 2>/dev/null || echo "Pillow not found"
