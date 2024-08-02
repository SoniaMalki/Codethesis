#!/bin/bash
#SBATCH --job-name=all_schedulings_master
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/scheduling/output_all_schedulings_master.txt
#SBATCH --ntasks=1
#SBATCH --time=2-00:00:00
#SBATCH --mem=2G

batch_scheduling_0_ID=$(sbatch /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/slurm_files/scheduling/batch/batch_scheduling_0.slurm | awk '{print $4}')
batch_scheduling_1_ID=$(sbatch --dependency=afterok:$batch_scheduling_0_ID /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/slurm_files/scheduling/batch/batch_scheduling_1.slurm | awk '{print $4}')
batch_scheduling_2_ID=$(sbatch --dependency=afterok:$batch_scheduling_1_ID /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/slurm_files/scheduling/batch/batch_scheduling_2.slurm | awk '{print $4}')

# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'scheduling' | grep -v 'all_schedulings_master' | wc -l) -gt 0 ]; do
  sleep 1
done

