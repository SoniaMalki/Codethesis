#!/bin/bash

script_dir=$(dirname "$0")
slurm_dir="$script_dir/slurm"

mkdir -p "$slurm_dir"/output/taskset "$slurm_dir"/output/assignment "$slurm_dir"/output/scheduling

python3 "$script_dir"/main.py generate_slurm_files

for slurm_file in "$slurm_dir"/slurm_files/taskset/*.slurm; do
  sbatch "$slurm_file"
done

for slurm_file in "$slurm_dir"/slurm_files/assignment/*.slurm; do
  taskset_id=$(basename "$slurm_file" .slurm)
  sbatch --dependency=afterok:"$taskset_id" "$slurm_file"
done

for slurm_file in "$slurm_dir"/slurm_files/scheduling/*.slurm; do
  assignment_id=$(basename "$slurm_file" .slurm)
  sbatch --dependency=afterok:"$assignment_id" "$slurm_file"
done