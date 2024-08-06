#!/bin/bash

# Nombre de jobs à lancer simultanément
MAX_JOBS=50

# Nom de l'expérience et type d'erreur, passés en arguments
EXPERIENCE=$1
ERROR_TYPE=$2

# Vérifier si les arguments sont fournis
if [ -z "$EXPERIENCE" ] || [ -z "$ERROR_TYPE" ]; then
  echo "Usage: $0 <experience_name> <error_type>"
  exit 1
fi

# Obtenir le chemin du script actuel
script_dir=$(dirname "$0")

# Dossier de base pour les fichiers d'erreur
ERROR_DIR="$script_dir/output_error/$ERROR_TYPE"

# Types de configuration
CONFIG_TYPES=("scheduling" "taskset" "assignment")

# Fonction pour compter les jobs en cours
count_jobs() {
  squeue -u $(whoami) | grep "PD\|R" | wc -l
}

# Vérifier si le dossier d'erreur existe
if [ ! -d "$ERROR_DIR" ]; then
  echo "Le dossier $ERROR_DIR n'existe pas."
  exit 1
fi

echo "Starting job submission for experience: $EXPERIENCE, error type: $ERROR_TYPE"

# Parcourir tous les fichiers dans le dossier d'erreur
for FILE in "$ERROR_DIR"/*; do
  # Extraire le nom de base du fichier
  BASENAME=$(basename "$FILE")
  
  # Extraire le nom du type de configuration et l'ID 
  CONFIG_TYPE=$(echo "$BASENAME" | sed -E 's/^output_([^_]+)_.*$/\1/')
  ID=$(echo "$BASENAME" | sed -E 's/^output_([^.]+).txt$/\1/')

  # Construire le chemin complet du fichier sbatch
  SBATCH_FILE="$script_dir/../../generation/$EXPERIENCE/slurm/slurm_files/$CONFIG_TYPE/$ID.slurm"

  echo "Processing error file: $FILE"
  echo "Configuration type: $CONFIG_TYPE, ID: $ID"
  echo "SBATCH file: $SBATCH_FILE"

  # Vérifier si le fichier sbatch existe
  if [ -f "$SBATCH_FILE" ]; then
    echo "Found SBATCH file: $SBATCH_FILE"

    # Attendre que le nombre de jobs actifs soit inférieur à MAX_JOBS
    while [ $(count_jobs) -ge $MAX_JOBS ]; do
      echo "Maximum number of jobs reached. Waiting..."
      sleep 10
    done

    # Lancer le script sbatch
    echo "Launching $SBATCH_FILE"
    sbatch "$SBATCH_FILE"
  else
    echo "Le fichier sbatch $SBATCH_FILE n'existe pas."
  fi
done

echo "Job submission completed for experience: $EXPERIENCE, error type: $ERROR_TYPE"
