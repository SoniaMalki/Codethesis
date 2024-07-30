#!/bin/bash

SOURCE="lemaitre4:~/Codethesis/"
DESTINATION="/home/sonia/Bureau/Codethesis/"

DIRECTORIES=(
    'config_files'
    'plots'
    'results'
)

for dir in "${DIRECTORIES[@]}"; do
    RSYNC_CMD="rsync -av ${SOURCE}${dir}/ ${DESTINATION}${dir}/"
    echo "Executing: $RSYNC_CMD"
    eval $RSYNC_CMD

    if [ $? -eq 0 ]; then
        echo "Transfer of ${dir} complete!"
    else
        echo "Transfer of ${dir} failed!"
    fi
done
