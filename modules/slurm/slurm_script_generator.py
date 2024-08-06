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
            f.write(f"echo \"Executing: {command}\"\n")
            f.write(f"{command}\n")
            f.write(
                f"echo \"Job completed: {job_name}_{self.experience_id}\"\n")

    def generate_all_scripts(self):
        print("Generating all SLURM scripts")
        self.create_script(
            script_name=f"generate_configs_{self.experience_id}.slurm",
            job_name="generate_configs",
            output_file=f"{self.output_slurm_path}/generate_configs_{self.experience_id}.txt",
            time="24:00:00",
            mem="16G",
            command=f"python3 {self.main_path}/main.py generate_configs {self.experience_id}"
        )

        self.create_script(
            script_name=f"generate_slurm_files_{self.experience_id}.slurm",
            job_name="generate_slurm_files",
            output_file=f"{self.output_slurm_path}/generate_slurm_files_{self.experience_id}.txt",
            time="24:00:00",
            mem="16G",
            command=f"python3 {self.main_path}/main.py generate_slurm_files {self.experience_id}"
        )

        self.create_script(
            script_name=f"submit_master_{self.experience_id}.slurm",
            job_name="submit_master",
            output_file=f"{self.output_slurm_path}/submit_master_{self.experience_id}.txt",
            time="00:10:00",
            mem="2G",
            command=f"echo \"Checking for master.slurm file\"\n"
                    f"MASTER_DIR=\"{self.generation_path}/{self.experience_id}/slurm/master\"\n"
                    "if [ -f \"$MASTER_DIR/master.slurm\" ]; then\n"
                    "    echo \"Submitting master.slurm\"\n"
                    "    sbatch \"$MASTER_DIR/master.slurm\"\n"
                    "else\n"
                    "    echo \"Erreur: $MASTER_DIR/master.slurm n'existe pas\"\n"
                    "    exit 1\n"
                    "fi\n"
        )

        self.create_script(
            script_name=f"analyze_results_{self.experience_id}.slurm",
            job_name="analyze_results",
            output_file=f"{self.output_slurm_path}/analyze_results_{self.experience_id}.txt",
            time="24:00:00",
            mem="16G",
            command=f"python3 {self.main_path}/main.py analyze_results {self.experience_id}"
        )

        self.create_script(
            script_name=f"full_pipeline_{self.experience_id}.slurm",
            job_name="full_pipeline",
            output_file=f"{self.output_slurm_path}/full_pipeline_{self.experience_id}.txt",
            time="24:00:00",
            mem="32G",
            command=f"echo \"Starting full pipeline for {self.experience_id}\"\n"
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
                    f"MASTER_DIR=\"{self.generation_path}/{self.experience_id}/slurm/master\"\n"
                    "if [ -f \"$MASTER_DIR/master.slurm\" ]; then\n"
                    "    echo \"Soumission du job master.slurm\"\n"
                    "    sbatch \"$MASTER_DIR/master.slurm\"\n"
                    "    if [ $? -ne 0 ]; then\n"
                    "        echo \"Échec de la soumission du job master.slurm\"\n"
                    "        exit 1\n"
                    "    fi\n"
                    "else\n"
                    "    echo \"Erreur: $MASTER_DIR/master.slurm n'existe pas\"\n"
                    "    exit 1\n"
                    "fi\n"
                    "echo \"Full pipeline completed for {self.experience_id}\"\n"
        )
        print("SLURM scripts generated successfully")


if __name__ == "__main__":
    pass
