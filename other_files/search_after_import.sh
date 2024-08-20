#!/bin/bash

# Vérifier les arguments
if [ $# -lt 3 ]; then
  echo "Usage: $0 <suffixe (nic5, lemaitre4, hercules, dragon2)> <experience_number> <config_type (all, taskset, assignment, scheduling)>"
  exit 1
fi

suffixe="$1"
experience_number="$2"
config_type="$3"

# Définir le chemin de base pour les scripts et les données
base_dir="$CODETHESIS"

# Gestion du chemin en fonction de la présence ou non d'un suffixe
if [ -z "$suffixe" ]; then
  output_dir="${GENERATION_DIR}/$experience_number/slurm/output"
  filtered_dir="$base_dir/error_handling/filtered_output"
else
  output_dir="${GENERATION_DIR}_${suffixe}/$experience_number/slurm/output"
  filtered_dir="$base_dir/error_handling/filtered_output_${suffixe}"
fi

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
  if [ -d "$output_path" ]; then
    echo "Processing directory: $output_path"
    # Trouver les fichiers .txt et les traiter
    find "$output_path" -type f -name "*.txt" -print0 | xargs -0 -I {} bash -c 'process_file "$@"' _ {}
  else
    echo "Dossier '$output_path' introuvable."
  fi
done

echo "Script execution completed."
