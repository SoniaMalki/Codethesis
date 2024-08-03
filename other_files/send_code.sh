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
    'generation'
    'output_error'
)

EXCLUDES=()
for item in "${EXCLUDE_ITEMS[@]}"; do
    if [[ "$item" == "slurm" || "$item" == "config_files" ]]; then
        EXCLUDES+=(--exclude=/"$item")
    else
        EXCLUDES+=(--exclude="$item")
    fi
done

RSYNC_CMD="rsync -av ${EXCLUDES[@]} $SOURCE $DESTINATION"

echo "Executing: $RSYNC_CMD"
eval $RSYNC_CMD

if [ $? -eq 0 ]; then
    echo "Transfer complete!"
else
    echo "Transfer failed!"
fi
