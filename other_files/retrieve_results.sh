#!/bin/bash

# Liste des clusters valides
VALID_CLUSTERS=("lemaitre4" "hercules" "nic5" "dragon2")

# Vérification du nom du cluster
CLUSTER_NAME=$1

if [[ -z "$CLUSTER_NAME" ]]; then
    echo "Erreur: Vous devez préciser un nom de cluster parmi les suivants : ${VALID_CLUSTERS[*]}"
    exit 1
fi

# Vérification si le cluster fourni est valide
if [[ ! " ${VALID_CLUSTERS[@]} " =~ " $CLUSTER_NAME " ]]; then
    echo "Erreur: Cluster invalide. Veuillez choisir parmi les suivants : ${VALID_CLUSTERS[*]}"
    exit 1
fi

SOURCE="$CLUSTER_NAME:~/Codethesis/"
DESTINATION="/home/sonia/Bureau/Codethesis/"

DIRECTORIES=(
    'generation'
)

for dir in "${DIRECTORIES[@]}"; do
    # Vérifier l'existence du répertoire source sur le serveur distant
    ssh "$CLUSTER_NAME" "test -d ~/Codethesis/$dir"
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
