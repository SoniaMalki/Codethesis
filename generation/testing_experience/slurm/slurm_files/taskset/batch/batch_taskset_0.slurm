#!/bin/bash
#SBATCH --job-name=batch_taskset_0
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/taskset/output_batch_taskset_0.txt
#SBATCH --ntasks=1
#SBATCH --time=00:00:01
#SBATCH --mem=2G

for config_key in taskset_generate_1_c4 taskset_generate_2_c4 taskset_generate_3_c4 taskset_generate_4_c4; do  # Séparer par des espaces
  sbatch /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/slurm_files/taskset/$config_key.slurm  # Utiliser le chemin complet
done

# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'taskset' | grep -v 'batch_taskset'| grep -v 'all_tasksets_master' | wc -l) -gt 0 ]; do
  sleep 1
done

                    