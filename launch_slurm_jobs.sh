#!/bin/bash

# Vérifier si un argument a été fourni
if [ -z "$1" ]; then
    echo "Erreur: Aucun nom de dossier fourni."
    echo "Usage: $0 <nom_du_dossier>"
    exit 1
fi

script_dir=$(dirname "$0")
experience_key=$1
experience_dir="$script_dir/generation/$experience_key"
master_dir="$experience_dir/slurm/master"


#[ -d "$experience_dir" ] && rm -rf "$experience_dir"

python3 "$script_dir/main.py" $experience_key generate_configs || { echo "Échec de la génération des configurations"; exit 1; }
python3 "$script_dir/main.py" $experience_key generate_slurm_files || { echo "Échec de la génération des fichiers Slurm"; exit 1; }

if [ -f "$master_dir/master.slurm" ]; then
    sbatch "$master_dir/master.slurm" || { echo "Échec de la soumission du job master.slurm"; exit 1; }
else
    echo "Erreur: $master_dir/master.slurm n'existe pas"
    exit 1
fi
