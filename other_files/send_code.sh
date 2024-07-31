#!/bin/bash

SOURCE="/home/sonia/Bureau/Codethesis/"
DESTINATION="lemaitre4:~/Codethesis"

EXCLUDE_ITEMS=(
    '.git'
    '__pycache__'
    'other_files'
    '.vscode'
    'tests'
    '.pytest_cache'
    '.gitignore'
    'README.md'
    'results'
    'plots'
    '*.slurm'
)

EXCLUDES=()
for item in "${EXCLUDE_ITEMS[@]}"; do
    EXCLUDES+=(--exclude="$item")
done

RSYNC_CMD="rsync -av ${EXCLUDES[@]} $SOURCE $DESTINATION"

echo "Executing: $RSYNC_CMD"
eval $RSYNC_CMD

if [ $? -eq 0 ]; then
    echo "Transfer complete!"
else
    echo "Transfer failed!"
fi
