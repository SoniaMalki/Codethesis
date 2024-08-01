#!/bin/bash

script_dir=$(dirname "$0")
experience_key=$1
master_dir="$script_dir/generation/$experience_key/slurm/master"

echo $script_dir
echo $master_dir
echo $experience_key

python3 "$script_dir/main.py" $experience_key generate_configs || { echo "Échec de la génération des configurations"; exit 1; }
python3 "$script_dir/main.py" $experience_key generate_slurm_files || { echo "Échec de la génération des fichiers Slurm"; exit 1; }

if [ -f "$master_dir/master.slurm" ]; then
    sbatch "$master_dir/master.slurm" || { echo "Échec de la soumission du job master.slurm"; exit 1; }
else
    echo "Erreur: $master_dir/master.slurm n'existe pas"
    exit 1
fi
