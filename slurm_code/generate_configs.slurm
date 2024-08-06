#!/bin/bash
#SBATCH --job-name=generate_configs
#SBATCH --output=slurm_code/output_launch_slurm_jobs/generate_configs_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=16G

# Vérifiez si un argument a été fourni
if [ -z "$1" ]; then
  echo "Erreur: Aucun argument fourni. Veuillez fournir un argument."
  echo "Usage: sbatch script.sh <argument>"
  exit 1
fi

# Utilisez l'argument fourni
ARGUMENT=$1

python3 "$HOME/Codethesis"/main.py generate_configs $ARGUMENT 
