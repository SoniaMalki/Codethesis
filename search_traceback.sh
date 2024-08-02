#!/bin/bash

# Vérifier les arguments
if [ $# -lt 2 ]; then
  echo "Usage: $0 <experience_number> <config_type (all, taskset, assignment, scheduling)>"
  exit 1
fi

experience_number="$1"
config_type="$2"

# Obtenir le chemin du script actuel
script_dir=$(dirname "$0")

# Chemin vers le dossier de sortie
output_dir="$script_dir/generation/$experience_number/slurm/output"
error_dir="$script_dir/output_error"

# Créer le dossier de sortie pour les erreurs s'il n'existe pas
mkdir -p "$error_dir"

# Fonction pour afficher le chemin d'un fichier et trier par type d'erreur
process_file() {
  local file_path="$1"
  local error_type

  # Déterminer le type d'erreur
  if grep -q "ZeroDivisionError" "$file_path"; then
    error_type="ZeroDivisionError"
  elif grep -q "TypeError" "$file_path"; then
    error_type="TypeError"
  else
    error_type="UnknownError"
  fi

  # Créer le dossier pour le type d'erreur s'il n'existe pas
  mkdir -p "$error_dir/$error_type"

  # Copier le fichier dans le dossier correspondant
  cp "$file_path" "$error_dir/$error_type/"
}

# Exporter la fonction pour qu'elle soit utilisable par xargs
export -f process_file
export error_dir

# Boucle sur les types de configuration
if [ "$config_type" == "all" ]; then
  config_types=("taskset" "assignment" "scheduling")
else
  config_types=("$config_type")
fi

for type in "${config_types[@]}"; do
  # Chemin vers le dossier de sortie pour le type de configuration
  output_path="$output_dir/$type"

  # Vérifier si le dossier existe
  if [ -d "$output_path" ]; then
    # Trouver les fichiers contenant "Traceback"
    find "$output_path" -type f -exec grep -q "Traceback" {} \; -print0 | xargs -0 -I {} bash -c 'process_file "$@"' _ {}
  else
    echo "Dossier '$output_path' introuvable."
  fi
done
