#!/bin/bash
#SBATCH --job-name=launch_slurm_jobs
#SBATCH --output=./launch_slurm_jobs.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=32G

./launch_slurm_jobs.sh full_experience
