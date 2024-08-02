#!/bin/bash
#SBATCH --job-name=batch_assignment
#SBATCH --output=/home/smalki/Codethesis/generation/estimation_experience/slurm/output/assignment/assignment_output_%A_%a.txt
#SBATCH --ntasks=1
#SBATCH --time=2:00:00
#SBATCH --mem=4G

# Définir les IDs d'expériences
exp_ids=(
  "assignment_generate_75_c8"
  "assignment_generate_1935_c4"
  "assignment_generate_243_c2"
  "assignment_generate_2214_c8"
  "assignment_generate_407_c4"
  "assignment_generate_2479_c2"
  "assignment_generate_646_c8"
  "assignment_generate_2283_c4"
  "assignment_generate_813_c2"
  "assignment_generate_2664_c8"
)

# Exécuter les expériences en séquence
for exp_id in "${exp_ids[@]}"; do
  sbatch /home/smalki/Codethesis/generation/estimation_experience/slurm/slurm_files/assignment/$exp_ids.slurm
done

# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'assignment' | grep -v 'batch_assignment' | wc -l) -gt 0 ]; do
  sleep 1
done