#!/bin/bash

# List of valid clusters and their corresponding $GLOBALSCRATCH paths
declare -A CLUSTER_GLOBALSCRATCH=(
    ["lemaitre4"]="/globalscratch/ulb/parts/smalki/"
    ["hercules"]="/workdir/smalki/"
    ["nic5"]="/scratch/ulb/parts/smalki/"
    ["dragon2"]="/home/ulb/parts/smalki/"
)

# Check the cluster name
CLUSTER_NAME=$1

# Correct check if the provided cluster is valid 
if [[ -z "${CLUSTER_GLOBALSCRATCH[$CLUSTER_NAME]+x}" ]]; then 
    echo "Error: Invalid cluster. Please choose from the following: ${!CLUSTER_GLOBALSCRATCH[@]}"
    exit 1
fi

GLOBALSCRATCH_PATH="${CLUSTER_GLOBALSCRATCH[$CLUSTER_NAME]}"

SOURCE="$CLUSTER_NAME:${GLOBALSCRATCH_PATH}"
DESTINATION="/home/sonia/Bureau/Codethesis/"

DIRECTORIES=(
    'generation'
)

for dir in "${DIRECTORIES[@]}"; do
    # Check existence of the source directory on the remote server
    ssh "$CLUSTER_NAME" "test -d ${GLOBALSCRATCH_PATH}/${dir}" # Using $GLOBALSCRATCH_PATH
    if [ $? -eq 0 ]; then
        # Construct the destination directory with cluster suffix
        DESTINATION_WITH_SUFFIX="${DESTINATION}${dir}_${CLUSTER_NAME}"

        # Create the destination directory if it does not exist
        if [ ! -d "$DESTINATION_WITH_SUFFIX" ]; then
            echo "Creating directory $DESTINATION_WITH_SUFFIX"
            mkdir -p "$DESTINATION_WITH_SUFFIX"
        fi

        # Simulate the transfer to estimate the data size
        RSYNC_DRY_RUN_CMD="rsync -av --dry-run --stats ${SOURCE}${dir}/ ${DESTINATION_WITH_SUFFIX}/"
        DRY_RUN_OUTPUT=$(eval $RSYNC_DRY_RUN_CMD)

        # Extract the total size of data to be transferred
        TOTAL_BYTES=$(echo "$DRY_RUN_OUTPUT" | grep "Total transferred file size" | awk '{print $5}' | sed 's/[.,]//g')

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

        echo "The total data size to be transferred for ${dir} from ${CLUSTER_NAME} is ${TOTAL_SIZE}${TOTAL_UNIT}."

        read -p "Do you want to proceed with the transfer? (y/n) " confirm
        if [[ "$confirm" != "y" ]]; then
            echo "Transfer aborted."
            exit 1
        fi

        RSYNC_CMD="rsync -avz --info=progress2 --no-whole-file -e 'ssh -T -c aes128-gcm@openssh.com -o Compression=no' ${SOURCE}${dir}/ $DESTINATION_WITH_SUFFIX/"
        echo "Executing: $RSYNC_CMD"
        eval $RSYNC_CMD

        if [ $? -eq 0 ]; then
            echo "Transfer of ${dir} from ${CLUSTER_NAME} complete!"
        else
            echo "Transfer of ${dir} from ${CLUSTER_NAME} failed!"
        fi
    else
        echo "Source directory ${SOURCE}${dir} does not exist on ${CLUSTER_NAME}. Skipping."
    fi
done