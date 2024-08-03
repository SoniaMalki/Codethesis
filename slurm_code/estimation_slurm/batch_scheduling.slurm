#!/bin/bash
#SBATCH --job-name=batch_scheduling
#SBATCH --output=/home/smalki/Codethesis/estimation_slurm/batch_scheduling.txt
#SBATCH --ntasks=1
#SBATCH --time=4:00:00
#SBATCH --mem=16G

# Define experience IDs
exp_ids=(
    "scheduling_generate_519_c8"
    "scheduling_generate_13543_c4"
    "scheduling_generate_1701_c2"
    "scheduling_generate_15493_c8"
    "scheduling_generate_2846_c4"
    "scheduling_generate_17353_c2"
    "scheduling_generate_4518_c8"
    "scheduling_generate_15979_c4"
    "scheduling_generate_5691_c2"
    "scheduling_generate_18643_c8"
)

# Execute experiences in sequence
for exp_id in "${exp_ids[@]}"; do
    sbatch /home/smalki/Codethesis/generation/estimation_experience/slurm/slurm_files/scheduling/${exp_id}.slurm
done

# Wait for all jobs to finish
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'scheduling' | grep -v 'batch_scheduling' | wc -l) -gt 0 ]; do
    sleep 1
done
