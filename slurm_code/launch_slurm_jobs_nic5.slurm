#!/bin/bash
#SBATCH --job-name=launch_slurm_jobs_%j
#SBATCH --output=/home/ulb/parts/smalki/Codethesis/slurm_code/output_launch_slurm_jobs/launch_slurm_jobs_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=32G

# Vérifiez si un argument a été fourni
if [ -z "$1" ]; then
  echo "Erreur: Aucun argument fourni. Veuillez fournir un argument."
  echo "Usage: sbatch script.sh <argument>"
  exit 1
fi

# Utilisez l'argument fourni
ARGUMENT=$1

"$HOME/Codethesis"/launch_slurm_jobs.sh $ARGUMENT
