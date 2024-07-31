#!/bin/bash
#SBATCH --job-name=master_job
#SBATCH --output="$slurm_dir"/output/master_job_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=04:00:00 
#SBATCH --mem=2G

slurm_dir=$1

for slurm_file in "$slurm_dir"/slurm_files/taskset/*.slurm; do
  sbatch "$slurm_file"
done

for slurm_file in "$slurm_dir"/slurm_files/taskset/*.slurm; do
  sbatch "$slurm_file"
done

last_taskset_job_id=$(squeue -u $USER -h -o "%A" | tail -n 1)

for slurm_file in "$slurm_dir"/slurm_files/assignment/*.slurm; do
  sbatch --dependency=afterok:"$last_taskset_job_id" "$slurm_file"
done

last_assignment_job_id=$(squeue -u $USER -h -o "%A" | tail -n 1)

for slurm_file in "$slurm_dir"/slurm_files/scheduling/*.slurm; do
  sbatch --dependency=afterok:"$last_assignment_job_id" "$slurm_file"
done