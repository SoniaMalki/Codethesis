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
    'permanent_results'
    'slurm_code/error_handling/output_error'
    'slurm_code/output_launch_slurm_jobs/'
    'slurm_code/slurm_scripts'
)

EXCLUDES=()
for item in "${EXCLUDE_ITEMS[@]}"; do
    EXCLUDES+=(--exclude="$item")
done

# Simuler le transfert pour estimer la taille des données
RSYNC_DRY_RUN_CMD="rsync -avz --dry-run --stats ${EXCLUDES[@]} $SOURCE $DESTINATION"
DRY_RUN_OUTPUT=$(eval $RSYNC_DRY_RUN_CMD)

# Extraire la taille totale des données à transférer
TOTAL_SIZE=$(echo "$DRY_RUN_OUTPUT" | grep "Total transferred file size" | awk '{print $5, $6}')
echo "The total data size to be transferred is ${TOTAL_SIZE}."

read -p "Do you want to proceed with the transfer? (y/n) " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Transfer aborted."
    exit 1
fi

RSYNC_CMD="rsync -avz --info=progress2 --no-whole-file --no-checksum -e 'ssh -T -c aes128-gcm@openssh.com -o Compression=no' ${EXCLUDES[@]} $SOURCE $DESTINATION"

echo "Executing: $RSYNC_CMD"
eval $RSYNC_CMD

if [ $? -eq 0 ]; then
    echo "Transfer complete!"
else
    echo "Transfer failed!"
fi
