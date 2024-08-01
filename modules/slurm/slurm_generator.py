from pathlib import Path
from datetime import time, timedelta
import json
from modules.core.experience_loader import ExperienceLoader


class SlurmGenerator:
    def __init__(self, main_dir, generation_dir, experience_key, experience_data):
        self.main_dir = Path(main_dir)
        self.generation_dir = Path(generation_dir)
        self.experience_key = experience_key

        # Vérifier si slurm_parameters est présent
        if "slurm_parameters" not in experience_data:
            raise ValueError(
                "slurm_parameters dictionary is missing in experience data."
            )

        self.slurm_parameters = experience_data["slurm_parameters"]

        self.master_dir = self.generation_dir / "slurm" / "master"
        self.slurm_dir = self.generation_dir / "slurm" / "slurm_files"
        self.output_dir = self.generation_dir / "slurm" / "output"

        for dir_path in [self.master_dir, self.slurm_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.experience_loader = ExperienceLoader(self.generation_dir)

        for config_type in ["taskset", "assignment", "scheduling"]:
            (self.slurm_dir / config_type).mkdir(parents=True, exist_ok=True)
            (self.output_dir / config_type).mkdir(parents=True, exist_ok=True)

    def get_slurm_content(self, config_key, config_type):
        # Convertir le temps du job en objet time
        job_time = time.fromisoformat(
            self.slurm_parameters.get(f"{config_type}_time", "02:00:00")
        )

        # Formater l'objet time en chaîne HH:MM:SS
        job_time_slurm = job_time.strftime("%H:%M:%S")
        return f"""#!/bin/bash
#SBATCH --job-name={config_key}
#SBATCH --output={self.output_dir / config_type / f"output_{config_key}.txt"}
#SBATCH --ntasks=1 
#SBATCH --time={job_time_slurm} 
#SBATCH --mem={self.slurm_parameters.get(f"{config_type}_mem", "8G")} 

# Charger les modules nécessaires
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0
module load GLPK/5.0-GCCcore-12.3.0
module load tis/2018.01
module load gurobi/gurobi1102

# Exécuter main.py avec la clé d'expérience en argument
python3 {self.main_dir / "main.py"} {self.experience_key} run_experience {config_key}
"""

    def generate_slurm(self, config_key, config_type):
        """Generate SLURM file for a specific configuration."""
        slurm_file = self.slurm_dir / config_type / f"{config_key}.slurm"
        with open(slurm_file, "w") as f:
            f.write(self.get_slurm_content(config_key, config_type))

    def get_wait_for_jobs_script(self, job_name, exclude_name):
        return f"""# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep '{job_name}' | grep -v '{exclude_name}' | wc -l) -gt 0 ]; do
  sleep 1
done
"""

    def write_master_slurm(self, config_type, total_time_slurm):
        """Write master SLURM file for a configuration type."""
        slurm_file = self.master_dir / f"all_{config_type}s.slurm"
        with open(slurm_file, "w") as f:
            f.write(
                f"""#!/bin/bash
#SBATCH --job-name=all_{config_type}s
#SBATCH --output={self.output_dir / config_type / f"output_all_{config_type}s_%j.txt"}
#SBATCH --ntasks=1
#SBATCH --time=2-00:00:00
#SBATCH --mem=2G 

for slurm_file in {self.slurm_dir / config_type}/*.slurm; do
  sbatch "$slurm_file"
done

{self.get_wait_for_jobs_script(config_type, f"all_{config_type}s")}
"""
            )

    def generate_master_slurm(self):
        """Generate the main master SLURM file."""
        slurm_file = self.master_dir / "master.slurm"
        with open(slurm_file, "w") as f:
            f.write(
                f"""#!/bin/bash
#SBATCH --job-name=master_job
#SBATCH --output={self.output_dir / f"master_job.txt"}
#SBATCH --ntasks=1
#SBATCH --time=00:02:00 
#SBATCH --mem=2G  

taskset_id=$(sbatch {self.master_dir / "all_tasksets.slurm"} | awk '{{print $4}}')
assignment_id=$(sbatch --dependency=afterok:$taskset_id {self.master_dir / "all_assignments.slurm"} | awk '{{print $4}}')
scheduling_id=$(sbatch --dependency=afterok:$assignment_id {self.master_dir / "all_schedulings.slurm"} | awk '{{print $4}}')
sbatch --dependency=afterok:$scheduling_id {self.master_dir / "analyze_results.slurm"}
"""
            )

    def generate_analyze_slurm(self):
        """Generate the SLURM file for analyzing results."""
        slurm_file = self.master_dir / "analyze_results.slurm"
        with open(slurm_file, "w") as f:
            f.write(
                f"""#!/bin/bash
#SBATCH --job-name=analyze_results
#SBATCH --output={self.output_dir / f"analyze_results.txt"}
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
#SBATCH --mem=4G

# Charger les modules nécessaires
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0

# Exécuter le script d'analyse
python3 {self.main_dir / "main.py"} {self.experience_key} analyze_results
"""
            )

    def generate_all_slurm(self):
        experience_loader = ExperienceLoader(self.generation_dir)
        for config_type in ["taskset", "assignment", "scheduling"]:
            config_file_path = experience_loader.config_files.get(config_type)
            with open(self.generation_dir / config_file_path, "r") as f:
                configurations = json.load(f)

            for config_key in configurations.keys():
                self.generate_slurm(config_key, config_type)

        # Générer les fichiers SLURM masters
        self.generate_master_slurm()

        # Générer le fichier SLURM pour l'analyse des résultats
        self.generate_analyze_slurm()
