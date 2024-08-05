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

# Annoncer le début de la génération des configurations
echo "Début de la génération des configurations pour $experience_key"

python3 "$script_dir/main.py" generate_configs $experience_key 
if [ $? -ne 0 ]; then
    echo "Échec de la génération des configurations"
    exit 1
else
    echo "Génération des configurations réussie"
fi

# Annoncer le début de la génération des fichiers Slurm
echo "Début de la génération des fichiers Slurm pour $experience_key"

python3 "$script_dir/main.py" generate_slurm_files $experience_key 
if [ $? -ne 0 ]; then
    echo "Échec de la génération des fichiers Slurm"
    exit 1
else
    echo "Génération des fichiers Slurm réussie"
fi

# Vérifier et soumettre le job master.slurm
if [ -f "$master_dir/master.slurm" ]; then
    echo "Soumission du job master.slurm"
    sbatch "$master_dir/master.slurm"
    if [ $? -ne 0 ]; then
        echo "Échec de la soumission du job master.slurm"
        exit 1
    else
        echo "Job master.slurm soumis avec succès"
    fi
else
    echo "Erreur: $master_dir/master.slurm n'existe pas"
    exit 1
fi
