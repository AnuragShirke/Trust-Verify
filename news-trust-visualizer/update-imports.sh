#!/bin/bash

# Find all files that import from "../../../utils.js"
files=$(grep -l "../../../utils.js" src/components/ui/*.tsx)

# Update each file
for file in $files; do
  echo "Updating $file"
  # Replace "../../../utils.js" with "./utils.js"
  sed -i 's|"../../../utils.js"|"./utils.js"|g' "$file"
done

echo "Import updates completed!"
