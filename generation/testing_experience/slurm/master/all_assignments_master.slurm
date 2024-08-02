#!/bin/bash
#SBATCH --job-name=all_assignments_master
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/assignment/output_all_assignments_master.txt
#SBATCH --ntasks=1
#SBATCH --time=2-00:00:00
#SBATCH --mem=2G

batch_assignment_0_ID=$(sbatch /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/slurm_files/assignment/batch/batch_assignment_0.slurm | awk '{print $4}')

# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'assignment' | grep -v 'all_assignments_master' | wc -l) -gt 0 ]; do
  sleep 1
done

