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

        # Simuler le transfert pour estimer la taille des données
        RSYNC_DRY_RUN_CMD="rsync -av --dry-run --stats ${SOURCE}${dir}/ ${DESTINATION}${dir}/"
        DRY_RUN_OUTPUT=$(eval $RSYNC_DRY_RUN_CMD)

        # Extraire la taille totale des données à transférer
        TOTAL_SIZE=$(echo "$DRY_RUN_OUTPUT" | grep "Total transferred file size" | awk '{print $5, $6}')
        echo "The total data size to be transferred for ${dir} is ${TOTAL_SIZE}."

        read -p "Do you want to proceed with the transfer? (y/n) " confirm
        if [[ "$confirm" != "y" ]]; then
            echo "Transfer aborted."
            exit 1
        fi

        RSYNC_CMD="rsync -av --info=progress2 ${SOURCE}${dir}/ ${DESTINATION}${dir}/"
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
