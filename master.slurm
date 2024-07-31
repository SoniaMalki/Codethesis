#!/bin/bash
#SBATCH --job-name=master_job
#SBATCH --output=/home/sonia/Bureau/Codethesis/slurm/output/master_job_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=12:00:00  
#SBATCH --mem=2G 

taskset_job_id=$(sbatch /home/sonia/Bureau/Codethesis/slurm/slurm_files/taskset/all_tasksets.slurm | awk '{print $4}')
echo "Taskset job submitted with ID $taskset_job_id"

assignment_job_id=$(sbatch --dependency=afterok:$taskset_job_id /home/sonia/Bureau/Codethesis/slurm/slurm_files/assignment/all_assignments.slurm | awk '{print $4}')
echo "Assignment job submitted with ID $assignment_job_id"

scheduling_job_id=$(sbatch --dependency=afterok:$assignment_job_id /home/sonia/Bureau/Codethesis/slurm/slurm_files/scheduling/all_schedulings.slurm | awk '{print $4}')
echo "Scheduling job submitted with ID $scheduling_job_id"
