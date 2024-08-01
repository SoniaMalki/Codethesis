#!/bin/bash

SOURCE="lemaitre4:~/Codethesis/"
DESTINATION="/home/sonia/Bureau/Codethesis/"

DIRECTORIES=(
    'generation'
)

for dir in "${DIRECTORIES[@]}"; do
    # Vérifier l'existence du répertoire source sur le serveur distant
    ssh lemaitre4 "test -d ~/Codethesis/$dir"
    if [ $? -eq 0 ]; then
        # Créer le répertoire de destination s'il n'existe pas
        if [ ! -d "${DESTINATION}${dir}" ]; then
            echo "Creating directory ${DESTINATION}${dir}"
            mkdir -p "${DESTINATION}${dir}"
        fi

        RSYNC_CMD="rsync -av ${SOURCE}${dir}/ ${DESTINATION}${dir}/"
        echo "Executing: $RSYNC_CMD"
        eval $RSYNC_CMD

        if [ $? -eq 0 ]; then
            echo "Transfer of ${dir} complete!"
        else
            echo "Transfer of ${dir} failed!"
        fi
    else
        echo "Source directory ${SOURCE}${dir} does not exist on the remote server. Skipping."
    fi
done
