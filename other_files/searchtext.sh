#!/bin/bash

# Ensure text to search is provided
if [ -z "$1" ]; then
  echo "Usage: $0 search_text"
  exit 1
fi

search_text="$1"

# Ensure CODETHESIS environment variable is set
if [ -z "$CODETHESIS" ]; then
  echo "Environment variable CODETHESIS is not set."
  exit 1
fi

# Define the directories to exclude
exclude_dirs="error_handling/output_error|error_handling/filtered_output"

# Find files containing the search text
files=$(grep -rl "$search_text" "$CODETHESIS" \
  --exclude-dir={.git,node_modules,cache,tmp,build,dist,.idea,.vscode,generation*} \
  --exclude=*.pyc \
  --exclude=*.class \
  --exclude=*.json \
  --exclude=*.pack \
  --exclude=*.jar \
  --exclude=*.woff \
  --exclude=*.zip \
  --exclude=*.wasm \
  --exclude=*.png \
  --exclude=*.git | grep -Ev "$exclude_dirs")

# If no files found, exit
if [ -z "$files" ]; then
  echo "No files found containing the text: $search_text"
  exit 0
fi

# Iterate through each file and open with Sublime Text
for file in $files; do
  echo "Opening file: $file"
  subl "$file"
  read -p "Press enter to open the next file..."
done

echo "All files opened."
