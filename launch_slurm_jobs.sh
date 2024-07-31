#!/bin/bash

script_dir=$(dirname "$0")
slurm_dir="$script_dir/slurm"
master_dir="$slurm_dir/master"

[ -d "$slurm_dir" ] && rm -rf "$slurm_dir"
[ -d "$script_dir/plots" ] && rm -rf "$script_dir/plots"
[ -d "$script_dir/results" ] && rm -rf "$script_dir/results"
[ -d "$script_dir/output" ] && rm -rf "$script_dir/output"

python3 "$script_dir/main.py" generate_configs || { echo "Échec de la génération des configurations"; exit 1; }
python3 "$script_dir/main.py" generate_slurm_files || { echo "Échec de la génération des fichiers Slurm"; exit 1; }

if [ -f "$master_dir/master.slurm" ]; then
    sbatch "$master_dir/master.slurm" || { echo "Échec de la soumission du job master.slurm"; exit 1; }
else
    echo "Erreur: $master_dir/master.slurm n'existe pas"
    exit 1
fi
