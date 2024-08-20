#!/bin/bash

# Nombre de jobs à lancer simultanément
MAX_JOBS=50

# Nom du suffixe, de l'expérience et type d'erreur, passés en arguments
SUFFIXE=$1
EXPERIENCE=$2
ERROR_TYPE=$3

# Vérifier si les arguments sont fournis
if [ -z "$SUFFIXE" ] || [ -z "$EXPERIENCE" ] || [ -z "$ERROR_TYPE" ]; then
  echo "Usage: $0 <suffixe (nic5, lemaitre4, hercules, dragon2)> <experience_name> <error_type>"
  exit 1
fi

# Définir le dossier de base pour les scripts et les données
base_dir="$CODETHESIS"

# Dossier de base pour les fichiers d'erreur
ERROR_DIR="$base_dir/error_handling/output_error/$ERROR_TYPE"

# Affichage pour debug
echo "Base directory: $base_dir"
echo "Error directory: $ERROR_DIR"

# Fonction pour compter les jobs en cours
count_jobs() {
  squeue -u $(whoami) | grep -c "PD\|R"
}

# Vérifier si le dossier d'erreur existe
if [ ! -d "$ERROR_DIR" ]; then
  echo "Le dossier $ERROR_DIR n'existe pas."
  exit 1
fi

echo "Starting job submission for experience: $EXPERIENCE, error type: $ERROR_TYPE, suffixe: $SUFFIXE"

# Parcourir tous les fichiers dans le dossier d'erreur
for FILE in "$ERROR_DIR"/*; do
  # Extraire le nom de base du fichier
  BASENAME=$(basename "$FILE")
  
  # Extraire le nom du type de configuration et l'ID 
  CONFIG_TYPE=$(echo "$BASENAME" | sed -E 's/([^_]+)_.*\.txt$/\1/')
  ID=$(echo "$BASENAME" | sed -E 's/[^_]+_([0-9]+)\.txt$/\1/')
  
  # Construire le chemin complet du fichier sbatch
  SBATCH_FILE="${GENERATION_DIR}_${SUFFIXE}/$EXPERIENCE/slurm/slurm_files/$CONFIG_TYPE/${CONFIG_TYPE}_${ID}.slurm"

  # Affichage pour debug
  echo "Processing error file: $FILE"
  echo "Configuration type: $CONFIG_TYPE, ID: $ID"
  echo "SBATCH file: $SBATCH_FILE"

  # Vérifier si le fichier sbatch existe
  if [ -f "$SBATCH_FILE" ]; then
    echo "Found SBATCH file: $SBATCH_FILE"

    # Attendre que le nombre de jobs actifs soit inférieur à MAX_JOBS
    while [ "$(count_jobs)" -ge $MAX_JOBS ]; do
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

echo "Job submission completed for experience: $EXPERIENCE, error type: $ERROR_TYPE, suffixe: $SUFFIXE"
