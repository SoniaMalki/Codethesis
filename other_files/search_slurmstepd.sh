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
  error_dir="$base_dir/error_handling/slurm_error"
else
  output_dir="${GENERATION_DIR}_${suffixe}/$experience_number/slurm/output"
  error_dir="$base_dir/error_handling/slurm_error_${suffixe}"
fi

# Créer le dossier de sortie pour les erreurs s'il n'existe pas
mkdir -p "$error_dir"

# Fonction pour afficher le chemin d'un fichier et trier par type d'arrêt
process_file() {
  local file_path="$1"
  local stop_type

  # Déterminer le type d'arrêt
  if grep -q "CANCELLED AT .* DUE TO TIME LIMIT" "$file_path"; then
    stop_type="TimeLimit"
  elif grep -q "CANCELLED AT .* DUE TO NODE FAILURE" "$file_path"; then
    stop_type="NodeFailure"
  elif grep -q "CANCELLED AT .* DUE TO USER REQUEST" "$file_path"; then
    stop_type="UserRequest"
  elif grep -q "CANCELLED AT .* DUE TO SYSTEM FAILURE" "$file_path"; then
    stop_type="SystemFailure"
  else
    stop_type="OtherReason"
  fi

  # Créer le dossier pour le type d'arrêt s'il n'existe pas
  mkdir -p "$error_dir/$stop_type"

  # Copier le fichier dans le dossier correspondant
  cp "$file_path" "$error_dir/$stop_type/"
  echo "Processed file: $file_path -> $stop_type"
}

# Exporter la fonction pour qu'elle soit utilisable par xargs
export -f process_file
export error_dir

# Boucle sur les types de configuration
if [ "$config_type" == "all" ]; then
  config_types=("")
else
  config_types=("$config_type")
fi

for type in "${config_types[@]}"; do
  if [ -n "$type" ];then
    # Chemin vers le dossier de sortie pour le type de configuration
    output_path="$output_dir/$type"
  else
    # Si type est vide, c'est la racine du dossier output
    output_path="$output_dir"
  fi

  # Vérifier si le dossier existe
  if [ -d "$output_path" ]; then
    echo "Processing directory: $output_path"
    # Trouver les fichiers contenant des messages SLURM d'arrêt de job
    find "$output_path" -type f -name "*.txt" -exec grep -q "slurmstepd: error:" {} \; -print0 | xargs -0 -I {} bash -c 'process_file "$@"' _ {}
  else
    echo "Dossier '$output_path' introuvable."
  fi
done

echo "Script execution completed."
