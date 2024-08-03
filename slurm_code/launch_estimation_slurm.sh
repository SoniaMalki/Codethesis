#!/bin/bash

# Vérifier si un argument a été fourni
if [ -z "$1" ]; then
    echo "Erreur: Aucune clé d'experience fournie."
    echo "Usage: $0 <clé_d'experience>"
    exit 1
fi

script_dir=$(dirname "$0")
experience_key=$1
experience_dir="$script_dir/generation/$experience_key"
estimation_dir="$script_dir/estimation_slurm"


[ -d "$experience_dir" ] && rm -rf "$experience_dir"
[ -d "$estimation_dir" ] && rm -rf "$estimation_dir"

python3 "$script_dir/main.py" $experience_key generate_configs || { echo "Échec de la génération des configurations"; exit 1; }
python3 "$script_dir/main.py" $experience_key generate_slurm_files || { echo "Échec de la génération des fichiers Slurm"; exit 1; }
python3 "$script_dir/main.py" $experience_key generate_estimation || { echo "Échec de la génération des Slurm d'estimation"; exit 1; }

if [ -f "$estimation_dir/master.slurm" ]; then
    sbatch "$estimation_dir/master.slurm" || { echo "Échec de la soumission du job master.slurm"; exit 1; }
else
    echo "Erreur: $estimation_dir/master.slurm n'existe pas"
    exit 1
fi
