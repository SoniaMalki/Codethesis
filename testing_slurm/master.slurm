#!/bin/bash
#SBATCH --job-name=master
#SBATCH --output=/home/smalki/Codethesis/testing_slurm/master_job.txt
#SBATCH --ntasks=1
#SBATCH --time=00:02:00
#SBATCH --mem=2G

taskset_id=$(sbatch /home/smalki/Codethesis/testing_slurm/batch_taskset.slurm | awk '{print $4}')
assignment_id=$(sbatch --dependency=afterok:$taskset_id /home/smalki/Codethesis/testing_slurm/batch_assignment.slurm | awk '{print $4}')
scheduling_id=$(sbatch --dependency=afterok:$assignment_id /home/smalki/Codethesis/testing_slurm/batch_scheduling.slurm | awk '{print $4}')
