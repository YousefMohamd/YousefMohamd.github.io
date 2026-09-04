#!/usr/bin/env bash

TARGET_INDEX_FILE="/Users/Yousef/my-portfolio/index.njk"
PROJECT_ROOT_DIRECTORY="/Users/Yousef/my-portfolio"

if [ -f "$TARGET_INDEX_FILE" ]; then
    sed -i '' 's/<source data-src=/<source data-srcset=/g' "$TARGET_INDEX_FILE"
    sed -i '' 's/<source src=/<source srcset=/g' "$TARGET_INDEX_FILE"
    echo "SUCCESS: Syntax correction applied to $TARGET_INDEX_FILE."
else
    echo "CRITICAL ERROR: File $TARGET_INDEX_FILE does not exist."
fi

find "$PROJECT_ROOT_DIRECTORY" -type f \( -name "*.njk" -o -name "*.json" \) -not -path "*/node_modules/*" -not -path "*/_site/*" -exec sed -i '' 's|/img/optimized/projects/|/img/projects/|g' {} +

echo "SUCCESS: Path correction applied strictly across all valid Nunjucks and JSON files."
