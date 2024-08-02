#!/bin/bash
#SBATCH --job-name=batch_assignment_0
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/assignment/output_batch_assignment_0.txt
#SBATCH --ntasks=1
#SBATCH --time=00:00:05
#SBATCH --mem=2G

for config_key in assignment_generate_1_c4 assignment_generate_2_c4 assignment_generate_3_c4 assignment_generate_4_c4 assignment_generate_5_c4 assignment_generate_6_c4 assignment_generate_7_c4 assignment_generate_8_c4 assignment_generate_9_c4 assignment_generate_10_c4 assignment_generate_11_c4 assignment_generate_12_c4 assignment_generate_13_c4 assignment_generate_14_c4 assignment_generate_15_c4 assignment_generate_16_c4 assignment_generate_17_c4 assignment_generate_18_c4 assignment_generate_19_c4 assignment_generate_20_c4 assignment_generate_21_c4 assignment_generate_22_c4 assignment_generate_23_c4 assignment_generate_24_c4 assignment_generate_25_c4 assignment_generate_26_c4 assignment_generate_27_c4 assignment_generate_28_c4 assignment_generate_29_c4 assignment_generate_30_c4 assignment_generate_31_c4 assignment_generate_32_c4; do  # Séparer par des espaces
  sbatch /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/slurm_files/assignment/$config_key.slurm  # Utiliser le chemin complet
done

# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'assignment' | grep -v 'batch_assignment'| grep -v 'all_assignments_master' | wc -l) -gt 0 ]; do
  sleep 1
done

                    