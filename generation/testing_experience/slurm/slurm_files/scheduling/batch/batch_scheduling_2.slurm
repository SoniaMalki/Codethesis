#!/bin/bash
#SBATCH --job-name=batch_scheduling_2
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/scheduling/output_batch_scheduling_2.txt
#SBATCH --ntasks=1
#SBATCH --time=00:30:00
#SBATCH --mem=2G

for config_key in scheduling_generate_201_c4 scheduling_generate_202_c4 scheduling_generate_203_c4 scheduling_generate_204_c4 scheduling_generate_205_c4 scheduling_generate_206_c4 scheduling_generate_207_c4 scheduling_generate_208_c4 scheduling_generate_209_c4 scheduling_generate_210_c4 scheduling_generate_211_c4 scheduling_generate_212_c4 scheduling_generate_213_c4 scheduling_generate_214_c4 scheduling_generate_215_c4 scheduling_generate_216_c4 scheduling_generate_217_c4 scheduling_generate_218_c4 scheduling_generate_219_c4 scheduling_generate_220_c4 scheduling_generate_221_c4 scheduling_generate_222_c4 scheduling_generate_223_c4 scheduling_generate_224_c4; do  # Séparer par des espaces
  sbatch /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/slurm_files/scheduling/$config_key.slurm  # Utiliser le chemin complet
done

# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'scheduling' | grep -v 'batch_scheduling'| grep -v 'all_schedulings_master' | wc -l) -gt 0 ]; do
  sleep 1
done

                    