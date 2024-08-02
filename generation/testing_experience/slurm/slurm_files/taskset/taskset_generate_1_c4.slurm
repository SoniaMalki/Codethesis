#!/bin/bash
#SBATCH --job-name=taskset_generate_1_c4
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/taskset/output_taskset_generate_1_c4.txt
#SBATCH --ntasks=1
#SBATCH --time=00:00:01
#SBATCH --mem=4G

# Charger les modules nécessaires
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0
module load GLPK/5.0-GCCcore-12.3.0
module load tis/2018.01
module load gurobi/gurobi1102

# Exécuter main.py avec la clé d'expérience en argument
python3 /home/sonia/Bureau/Codethesis/main.py testing_experience run_experience taskset_generate_1_c4
