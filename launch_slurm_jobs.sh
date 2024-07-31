#!/bin/bash

script_dir=$(dirname "$0")
slurm_dir="$script_dir/slurm"
master_dir="$slurm_dir/master"

rm -rf $slurm_dir
rm -rf "$script_dir/plots"
rm -rf "$script_dir/results"
rm -rf "$script_dir/output"
rm "$master_dir/master.slurm"

python3 "$script_dir"/main.py generate_configs
python3 "$script_dir"/main.py generate_slurm_files

sbatch "$master_dir"/master.slurm 