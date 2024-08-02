#!/bin/bash
#SBATCH --job-name=analyze_results
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/analyze_results.txt
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
#SBATCH --mem=4G

# Charger les modules nécessaires
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0

# Exécuter le script d'analyse
python3 /home/sonia/Bureau/Codethesis/main.py testing_experience analyze_results
