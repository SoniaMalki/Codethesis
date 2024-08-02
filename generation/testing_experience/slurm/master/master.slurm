#!/bin/bash
#SBATCH --job-name=master_job
#SBATCH --output=/home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/output/master_job.txt
#SBATCH --ntasks=1
#SBATCH --time=00:02:00
#SBATCH --mem=2G

taskset_id=$(sbatch /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/master/all_tasksets_master.slurm | awk '{print $4}')
assignment_id=$(sbatch --dependency=afterok:$taskset_id /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/master/all_assignments_master.slurm | awk '{print $4}')
scheduling_id=$(sbatch --dependency=afterok:$assignment_id /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/master/all_schedulings_master.slurm | awk '{print $4}')
sbatch --dependency=afterok:$scheduling_id /home/sonia/Bureau/Codethesis/generation/testing_experience/slurm/master/analyze_results.slurm
