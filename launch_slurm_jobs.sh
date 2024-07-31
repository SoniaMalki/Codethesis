#!/bin/bash

script_dir=$(dirname "$0")
slurm_dir="$script_dir/slurm"

rm -rf $slurm_dir
mkdir $slurm_dir

mkdir -p "$slurm_dir"/output/taskset "$slurm_dir"/output/assignment "$slurm_dir"/output/scheduling

python3 "$script_dir"/main.py generate_slurm_files

sbatch "$script_dir"/master.slurm "$slurm_dir"