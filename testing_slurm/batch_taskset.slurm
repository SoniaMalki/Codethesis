#!/bin/bash
#SBATCH --job-name=batch_taskset
#SBATCH --output=/home/smalki/Codethesis/generation/estimation_experience/slurm/output/taskset/batch_taskset_output.txt
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --mem=2G


# Définir les IDs d'expériences
exp_ids=(
  "taskset_generate_3_c8"
  "taskset_generate_53_c4"
  "taskset_generate_7_c2"
  "taskset_generate_60_c8"
  "taskset_generate_11_c4"
  "taskset_generate_67_c2"
  "taskset_generate_18_c8"
  "taskset_generate_62_c4"
  "taskset_generate_22_c2"
  "taskset_generate_72_c8"
)

# Exécuter les expériences en séquence
for exp_id in "${exp_ids[@]}"; do
  sbatch /home/smalki/Codethesis/generation/estimation_experience/slurm/slurm_files/taskset/$exp_ids.slurm
done

# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'taskset' | grep -v 'batch_taskset' | wc -l) -gt 0 ]; do
  sleep 1
done