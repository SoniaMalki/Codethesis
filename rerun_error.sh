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

# Dossier de base pour les fichiers d'erreur
ERROR_DIR="./output_error/$ERROR_TYPE"

# Dossier de base pour les fichiers sbatch
SBATCH_DIR="./generation/$EXPERIENCE/slurm/slurm_files/scheduling"

# Vérifier si le dossier d'erreur existe
if [ ! -d "$ERROR_DIR" ]; then
  echo "Le dossier $ERROR_DIR n'existe pas."
  exit 1
fi

# Fonction pour compter les jobs en cours
count_jobs() {
  squeue -u $(whoami) | grep "PD\|R" | wc -l
}

# Parcourir tous les fichiers dans le dossier d'erreur
for FILE in $ERROR_DIR/*; do
  # Extraire le nom de base du fichier
  BASENAME=$(basename "$FILE")
  
  # Extraire l'identifiant du fichier, en supposant qu'il est au format output_scheduling_generate_8302_c4.txt
  ID=$(echo "$BASENAME" | sed -E 's/output_scheduling_generate_([^.]+)\.txt/\1/')

  # Construire le chemin complet du fichier sbatch
  SBATCH_FILE="$SBATCH_DIR/scheduling_generate_$ID.slurm"

  # Vérifier si le fichier sbatch existe
  if [ -f "$SBATCH_FILE" ]; then
    # Attendre que le nombre de jobs actifs soit inférieur à MAX_JOBS
    while [ $(count_jobs) -ge $MAX_JOBS ]; do
      sleep 10
    done

    # Lancer le script sbatch
    echo "Lancement de $SBATCH_FILE"
    sbatch "$SBATCH_FILE"
  else
    echo "Le fichier sbatch $SBATCH_FILE n'existe pas."
  fi
done
