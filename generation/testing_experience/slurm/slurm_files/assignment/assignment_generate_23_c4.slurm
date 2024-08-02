#!/bin/bash
#SBATCH --job-name=assignment_generate_23_c4
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/assignment/output_assignment_generate_23_c4.txt
#SBATCH --ntasks=1
#SBATCH --time=00:00:05
#SBATCH --mem=16G

# Charger les modules nécessaires
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0
module load GLPK/5.0-GCCcore-12.3.0
module load tis/2018.01
module load gurobi/gurobi1102

# Exécuter main.py avec la clé d'expérience en argument
python3 /home/sonia/Bureau/Codethesis/main.py testing_experience run_experience assignment_generate_23_c4
