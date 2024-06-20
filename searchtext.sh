#!/bin/bash

# Ensure text to search is provided
if [ -z "$1" ]; then
  echo "Usage: $0 search_text"
  exit 1
fi

search_text="$1"

# Find files containing the search text, excluding specified extensions
files=$(grep -rl --exclude=*.class --exclude=*.json --exclude=*.pack "$search_text" .)

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
