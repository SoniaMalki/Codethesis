#!/bin/bash

script_dir=$(dirname "$0")
echo $script_dir

mkdir -p "$script_dir"/output/taskset "$script_dir"/output/assignment "$script_dir"/output/scheduling

python3 "$script_dir"/../main.py generate_slurm_files

for slurm_file in "$script_dir"/slurm_files/taskset/*.slurm; do
  echo "$slurm_file"
done

for slurm_file in "$script_dir"/slurm_files/assignment/*.slurm; do
  taskset_id=$(basename "$slurm_file" .slurm)
  echo --dependency=afterok:"$taskset_id" "$slurm_file"
done

for slurm_file in "$script_dir"/slurm_files/scheduling/*.slurm; do
  assignment_id=$(basename "$slurm_file" .slurm)
  echo --dependency=afterok:"$assignment_id" "$slurm_file"
done