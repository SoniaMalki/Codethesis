#!/bin/bash

# List of valid clusters
VALID_CLUSTERS=("lemaitre4" "hercules" "nic5" "dragon2")

# Check the cluster name
CLUSTER_NAME=$1

if [[ -z "$CLUSTER_NAME" ]]; then
    echo "Error: You must specify a cluster name among the following: ${VALID_CLUSTERS[*]}"
    exit 1
fi

# Check if the provided cluster is valid
if [[ ! " ${VALID_CLUSTERS[@]} " =~ " $CLUSTER_NAME " ]]; then
    echo "Error: Invalid cluster. Please choose from the following: ${VALID_CLUSTERS[*]}"
    exit 1
fi

SOURCE="/home/sonia/Bureau/Codethesis/"
DESTINATION="$CLUSTER_NAME:~/Codethesis"

EXCLUDE_ITEMS=(
    '.git'
    '__pycache__'
    'other_files'
    '.vscode'
    'tests'
    '.pytest_cache'
    '.gitignore'
    'README.md'
    'permanent_results'
    '/error_handling/output_error'
    '/error_handling/filtered_output'
)

EXCLUDES=()
for item in "${EXCLUDE_ITEMS[@]}"; do
    EXCLUDES+=(--exclude="$item")
done

# Simulate the transfer to estimate the data size
RSYNC_DRY_RUN_CMD="rsync -avz --dry-run --stats ${EXCLUDES[@]} $SOURCE $DESTINATION"
DRY_RUN_OUTPUT=$(eval $RSYNC_DRY_RUN_CMD)

# Extract the total size of data to be transferred
TOTAL_BYTES=$(echo "$DRY_RUN_OUTPUT" | grep "Total transferred file size" | awk '{print $5}' | sed 's/[.,]//g') # Remove commas and dots

# Convert the size to an appropriate unit
if [ $TOTAL_BYTES -ge 1073741824 ]; then
    TOTAL_SIZE=$(echo "scale=2; $TOTAL_BYTES/1073741824" | bc) && TOTAL_UNIT="GB"
elif [ $TOTAL_BYTES -ge 1048576 ]; then
    TOTAL_SIZE=$(echo "scale=2; $TOTAL_BYTES/1048576" | bc) && TOTAL_UNIT="MB"
elif [ $TOTAL_BYTES -ge 1024 ]; then
    TOTAL_SIZE=$(echo "scale=2; $TOTAL_BYTES/1024" | bc) && TOTAL_UNIT="KB"
else
    TOTAL_SIZE=$TOTAL_BYTES && TOTAL_UNIT="B"
fi

echo "The total data size to be transferred is ${TOTAL_SIZE}${TOTAL_UNIT}."

read -p "Do you want to proceed with the transfer? (y/n) " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Transfer aborted."
    exit 1
fi

RSYNC_CMD="rsync -avz --info=progress2 --no-whole-file -e 'ssh -T -c aes128-gcm@openssh.com -o Compression=no' ${EXCLUDES[@]} $SOURCE $DESTINATION"

echo "Executing: $RSYNC_CMD"
eval $RSYNC_CMD

if [ $? -eq 0 ]; then
    echo "Transfer complete!"
else
    echo "Transfer failed!"
fi

