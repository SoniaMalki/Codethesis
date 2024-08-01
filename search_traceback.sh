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

# Fonction pour afficher le chemin d'un fichier
echo_file_path() {
  local file_path="$1"
  echo "$file_path"
}

# Exporter la fonction pour qu'elle soit utilisable par xargs
export -f echo_file_path

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
    find "$output_path" -type f -exec grep -q "Traceback" {} \; -print0 | xargs -0 -I {} bash -c 'echo_file_path "$@"' _ {}
  else
    echo "Dossier '$output_path' introuvable."
  fi
done
