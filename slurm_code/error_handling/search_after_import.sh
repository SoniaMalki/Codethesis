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
output_dir="$script_dir/../../generation/$experience_number/slurm/output"
filtered_dir="$script_dir/filtered_output"

# Créer le dossier de sortie pour les fichiers filtrés s'il n'existe pas
mkdir -p "$filtered_dir"

# Fonction pour traiter les fichiers
process_file() {
  local file_path="$1"
  
  # Contenu à vérifier
  content_to_check=$(cat <<EOF
Gurobi shell based on Python 3.10.8 can be launched with command \`gurobi.sh\`
Gurobi Python Interface can be loaded in Python 3.10.8 with 'import gurobipy'
Gurobi shell based on Python 3.10.8 can be launched with command \`gurobi.sh\`
Gurobi Python Interface can be loaded in Python 3.10.8 with 'import gurobipy'
EOF
)

  # Vérifier si le fichier contient exactement le contenu à vérifier
  if ! cmp -s <(echo "$content_to_check") "$file_path"; then
    # Si le contenu est différent, on considère qu'il contient autre chose
    cp "$file_path" "$filtered_dir/"
    echo "Processed file: $file_path -> moved to filtered_output"
  fi
}

# Exporter la fonction pour qu'elle soit utilisable par xargs
export -f process_file
export filtered_dir

# Boucle sur les types de configuration
if [ "$config_type" == "all" ]; then
  config_types=("taskset" "assignment" "scheduling" "")
else
  config_types=("$config_type")
fi

for type in "${config_types[@]}"; do
  if [ -n "$type" ]; then
    # Chemin vers le dossier de sortie pour le type de configuration
    output_path="$output_dir/$type"
  else
    # Si type est vide, c'est la racine du dossier output
    output_path="$output_dir"
  fi

  # Vérifier si le dossier existe
  if [ -d "$output_path" ];then
    echo "Processing directory: $output_path"
    # Trouver les fichiers .txt et les traiter
    find "$output_path" -type f -name "*.txt" -print0 | xargs -0 -I {} bash -c 'process_file "$@"' _ {}
  else
    echo "Dossier '$output_path' introuvable."
  fi
done

echo "Script execution completed."

