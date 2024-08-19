#!/bin/bash
#SBATCH --time=2-00:00:00
#SBATCH --output=./create_full_pipeline_output.txt
#SBATCH --job-name=create_full_pipeline

if [[ $(hostname) == *"her" ]]; then
    module load Python/3.9.6-GCCcore-11.2.0
    module load GLPK/5.0-GCCcore-11.2.0
    module load Gurobi-Optimizer/9.5.1

elif [[ $(hostname) == *"lm4" ]]; then
    module load releases/2023a
    module load Python/3.11.3-GCCcore-12.3.0
    module load GLPK/5.0-GCCcore-12.3.0
    module load tis/2018.01
    module load gurobi/gurobi1102

elif [[ $(hostname) == *"nic" ]]; then
    module load releases/2022b
    module load Python/3.10.8-GCCcore-12.2.0
    module load GLPK/5.0-GCCcore-12.2.0
    module load Gurobi/10.0.3-GCCcore-12.2.0
fi

# Exécute le script Python pour générer les scripts SLURM
echo "Launching python generate_slurm_scripts"
echo "--------PYTHON-OUTPUT-BEGIN------------------"
python3 -u $HOME/Codethesis/main.py generate_slurm_scripts $1
echo "--------PYTHON-OUTPUT-END--------------------"
echo "Python generate slurm script finish."

# Soumet le script généré en tant que job
echo "Launching fullpipeline"
echo "--------SBATCH-OUTPUT-BEGIN------------------"

# Utiliser un fichier temporaire pour capturer stdout et stderr
tempfile=$(mktemp)

# Soumission du job et capture de la sortie et des erreurs
sbatch "$HOME/Codethesis/generation/$1/slurm/master/full_pipeline_$1.slurm" >"$tempfile" 2>&1
output=$(cat "$tempfile")

# Vérifier s'il y a une erreur dans la sortie
if echo "$output" | grep -q "error"; then
    # Afficher l'erreur et quitter
    echo "Job not launched. Output:"
    echo "$output"
else
    # Extraire le Job ID de la sortie de sbatch
    job_id=$(echo "$output" | awk '{print $4}')

    # Vérifier si le Job ID est valide
    if [[ -n "$job_id" ]]; then
        # Extraire le nom du job en utilisant scontrol
        job_name=$(scontrol show job "$job_id" | grep "JobName=" | awk -F= '{print $3}')

        # Afficher le message original et le nom du job
        echo "$output | Job Name: $job_name"
    else
        # Si le job n'a pas été lancé, afficher un message d'erreur
        echo "Job not launched. Output:"
        echo "$output"
    fi
fi

# Nettoyer le fichier temporaire
rm -f "$tempfile"
echo "--------SBATCH-OUTPUT-END------------------"

