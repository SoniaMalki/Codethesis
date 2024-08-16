import os


class SlurmScriptGenerator:
    def __init__(self, main_path, slurm_script_path, output_slurm_path, generation_path, experience_id):
        print("Initializing SlurmScriptGenerator")
        self.main_path = main_path
        self.slurm_script_path = slurm_script_path
        self.output_slurm_path = output_slurm_path
        self.generation_path = generation_path
        os.makedirs(self.slurm_script_path, exist_ok=True)
        os.makedirs(self.output_slurm_path, exist_ok=True)
        os.makedirs(self.generation_path, exist_ok=True)
        self.experience_id = experience_id
        print("SlurmScriptGenerator initialized successfully")

    def create_script(self, script_name, job_name, output_file, time, mem, command):
        script_path = os.path.join(self.slurm_script_path, script_name)
        with open(script_path, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"#SBATCH --job-name={job_name}_{self.experience_id}\n")
            f.write(f"#SBATCH --output={output_file}\n")
            f.write("#SBATCH --ntasks=1\n")
            f.write(f"#SBATCH --time={time}\n")
            f.write(f"#SBATCH --mem={mem}\n\n")

            f.write(
                f"echo \"Starting job: {job_name}_{self.experience_id}\"\n")
            f.write(command)
            f.write(
                f"\necho \"Job completed: {job_name}_{self.experience_id}\"\n")

    def generate_all_scripts(self):
        print("Generating all SLURM scripts")

        # Full Pipeline Script with Integrated Master Logic and Updated Time/Memory
        self.create_script(
            script_name=f"full_pipeline_{self.experience_id}.slurm",
            job_name="full_pipeline",
            output_file=f"{self.output_slurm_path}/full_pipeline_{self.experience_id}.txt",
            time="2-00:00:00",  # Updated time
            mem="4G",  # Updated memory
            command=(
                f"echo \"Starting full pipeline for {self.experience_id}\"\n"
                f"python3 {self.main_path}/main.py generate_configs {self.experience_id}\n"
                "if [ $? -ne 0 ]; then\n"
                "    echo \"Échec de la génération des configurations\"\n"
                "    exit 1\n"
                "fi\n\n"
                "echo \"Génération des configurations réussie\"\n"
                f"python3 {self.main_path}/main.py generate_slurm_files {self.experience_id}\n"
                "if [ $? -ne 0 ]; then\n"
                "    echo \"Échec de la génération des fichiers SLURM\"\n"
                "    exit 1\n"
                "fi\n\n"
                "echo \"Génération des fichiers SLURM réussie\"\n"
                "echo \"Starting master job\"\n"
                f"MASTER_DIR=\"{self.generation_path}/{self.experience_id}/slurm/master\"\n"

                # Taskset
                "if [ -f \"$MASTER_DIR/all_tasksets_master.slurm\" ]; then\n"
                "  echo \"Submitting all_tasksets_master.slurm\"\n"
                "  taskset_id=$(sbatch \"$MASTER_DIR/all_tasksets_master.slurm\" | awk '{print $4}')\n"
                "fi\n"

                # Assignment (dependent on taskset)
                "if [ -f \"$MASTER_DIR/all_assignments_master.slurm\" ]; then\n"
                "  echo \"Submitting all_assignments_master.slurm\"\n"
                "  if [[ -z \"$taskset_id\" ]]; then\n"
                "    assignment_id=$(sbatch \"$MASTER_DIR/all_assignments_master.slurm\" | awk '{print $4}')\n"
                "  else\n"
                "    assignment_id=$(sbatch --dependency=afterok:$taskset_id \"$MASTER_DIR/all_assignments_master.slurm\" | awk '{print $4}')\n"
                "  fi\n"
                "fi\n"

                # Scheduling (dependent on assignment OR taskset if assignment failed)
                "if [ -f \"$MASTER_DIR/all_schedulings_master.slurm\" ]; then\n"
                "  echo \"Submitting all_schedulings_master.slurm\"\n"
                "  if [[ -z \"$assignment_id\" && -n \"$taskset_id\" ]]; then\n"
                "    scheduling_id=$(sbatch --dependency=afterok:$taskset_id \"$MASTER_DIR/all_schedulings_master.slurm\" | awk '{print $4}')\n"
                "  elif [[ -n \"$assignment_id\" ]]; then\n"
                "    scheduling_id=$(sbatch --dependency=afterok:$assignment_id \"$MASTER_DIR/all_schedulings_master.slurm\" | awk '{print $4}')\n"
                "  else\n"
                "    scheduling_id=$(sbatch \"$MASTER_DIR/all_schedulings_master.slurm\" | awk '{print $4}')\n"
                "  fi\n"
                "fi\n"

                # Analyze Results (directly in Python)
                "echo \"Analyzing results directly in Python\"\n"
                f"python3 {self.main_path}/main.py analyze_results {self.experience_id}\n"

                f"echo \"Full pipeline completed for {self.experience_id}\"\n"
            )
        )
        print("SLURM scripts generated successfully")


if __name__ == "__main__":
    pass
