from pathlib import Path
from datetime import time
import json
import socket
from modules.core.experience_loader import ExperienceLoader


class SlurmGenerator:
    def __init__(self, main_path, generation_path, db_path, experience_id, experience_data, batch_size=100):
        print("Initializing SlurmGenerator")
        self.main_path = Path(main_path)
        self.generation_path = Path(generation_path) / experience_id
        self.db_path = db_path
        self.experience_id = experience_id
        self.batch_size = batch_size

        # Vérifier si slurm_parameters est présent
        if "slurm_parameters" not in experience_data:
            raise ValueError(
                "slurm_parameters dictionary is missing in experience data."
            )

        self.slurm_parameters = experience_data["slurm_parameters"]

        self.master_dir = self.generation_path / "slurm" / "master"
        self.slurm_dir = self.generation_path / "slurm" / "slurm_files"
        self.output_dir = self.generation_path / "slurm" / "output"
        print(f"DB path: {self.db_path}")

        for dir_path in [self.master_dir, self.slurm_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.experience_loader = ExperienceLoader(
            self.db_path, self.experience_id)

        # Dictionnaire des modules pour chaque cluster
        self.cluster_modules = {
            "lm": """
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0
module load GLPK/5.0-GCCcore-12.3.0
module load tis/2018.01
module load gurobi/gurobi1102
""",
            "her": """
module load Python/3.9.6-GCCcore-11.2.0
module load GLPK/5.0-GCCcore-11.2.0
module load Gurobi-Optimizer/9.5.1
""",
            "nic": """
module load releases/2022b
module load Python/3.10.8-GCCcore-12.2.0
module load GLPK/5.0-GCCcore-12.2.0
module load Gurobi/10.0.3-GCCcore-12.2.0
""",
        }
        # Récupérer le hostname de la machine
        hostname = socket.gethostname()
        print(f"Hostname: {hostname}")
        # Charger les modules en fonction du cluster
        self.modules = self.get_modules_for_hostname(hostname)
        print(f"Loaded modules: {self.modules}")

        for config_type in ["taskset", "assignment", "scheduling"]:
            (self.slurm_dir / config_type).mkdir(parents=True, exist_ok=True)
            (self.slurm_dir / config_type /
             "batch").mkdir(parents=True, exist_ok=True)
            (self.output_dir / config_type).mkdir(parents=True, exist_ok=True)

        print("SlurmGenerator initialized successfully")

    def get_modules_for_hostname(self, hostname):
        for key in self.cluster_modules.keys():
            if hostname.startswith(key):
                return self.cluster_modules[key]
        return ""

    def get_slurm_content(self, config_key, config_type):
        # Convertir le temps du job en objet time
        job_time = time.fromisoformat(
            self.slurm_parameters.get(f"{config_type}_time", "02:00:00")
        ).strftime("%H:%M:%S")
        return f"""#!/bin/bash
#SBATCH --job-name={config_key}
#SBATCH --output={self.output_dir / config_type / f"output_{config_key}.txt"}
#SBATCH --ntasks=1
#SBATCH --time={job_time}
#SBATCH --mem={self.slurm_parameters.get(f"{config_type}_mem", "8G")}

# Charger les modules nécessaires
{self.modules}

# Exécuter main.py avec la clé d'expérience en argument
python3 {self.main_path}/main.py run_experience {self.experience_id} {config_key}
"""

    def generate_slurm(self, config_key, config_type):
        """Generate SLURM file for a specific configuration."""
        print(f"Generating SLURM file for {config_key} of type {config_type}")
        slurm_file = self.slurm_dir / config_type / f"{config_key}.slurm"
        with open(slurm_file, "w") as f:
            f.write(self.get_slurm_content(config_key, config_type))
        print(f"SLURM file for {config_key} generated at {slurm_file}")

    def get_wait_for_jobs_script(self, job_name, exclude_name):
        if type(exclude_name) != list:
            exclude_name = [exclude_name]

        grep_command = [
            f"| grep -v '{ex_name}'" for ex_name in exclude_name]
        grep_command = ''.join(grep_command)

        return f"""# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep '{job_name}' {grep_command} | wc -l) -gt 0 ]; do
  sleep 1
done
"""

    def write_master_slurm(self, config_type):
        """Write master SLURM file for a configuration type."""
        print(f"Writing master SLURM file for {config_type}")
        slurm_file = self.master_dir / f"all_{config_type}s_master.slurm"
        batch_files = sorted(
            (self.slurm_dir / config_type / "batch").glob("*.slurm")
        )

        with open(slurm_file, "w") as f:
            f.write(
                f"""#!/bin/bash
#SBATCH --job-name=all_{config_type}s_master
#SBATCH --output={self.output_dir / config_type / f"output_all_{config_type}s_master.txt"}
#SBATCH --ntasks=1
#SBATCH --time=2-00:00:00
#SBATCH --mem=2G

"""
            )

            # Lancer les batchs avec dépendances
            previous_batch_id_var = None
            for i, batch_file in enumerate(batch_files):
                batch_name = batch_file.stem
                current_batch_id_var = f"{batch_name}_ID"

                if previous_batch_id_var:
                    f.write(
                        f"""{current_batch_id_var}=$(sbatch --dependency=afterok:${previous_batch_id_var} {batch_file} | awk '{{print $4}}')\n"""
                    )
                else:
                    f.write(
                        f"""{current_batch_id_var}=$(sbatch {batch_file} | awk '{{print $4}}')\n"""
                    )
                previous_batch_id_var = current_batch_id_var

            f.write(
                f"""
{self.get_wait_for_jobs_script(config_type, f"all_{config_type}s_master")}
"""
            )
        print(f"Master SLURM file for {config_type} written at {slurm_file}")

    def generate_master_slurm(self):
        """Generate the main master SLURM file."""
        print("Generating the main master SLURM file")
        for config_type in ["taskset", "assignment", "scheduling"]:
            self.write_master_slurm(config_type)

        slurm_file = self.master_dir / "master.slurm"
        with open(slurm_file, "w") as f:
            f.write(
                f"""#!/bin/bash
#SBATCH --job-name=master_job
#SBATCH --output={self.output_dir / f"master_job.txt"}
#SBATCH --ntasks=1
#SBATCH --time=00:02:00
#SBATCH --mem=2G

taskset_id=$(sbatch {self.master_dir / "all_tasksets_master.slurm"} | awk '{{print $4}}')
assignment_id=$(sbatch --dependency=afterok:$taskset_id {self.master_dir / "all_assignments_master.slurm"} | awk '{{print $4}}')
scheduling_id=$(sbatch --dependency=afterok:$assignment_id {self.master_dir / "all_schedulings_master.slurm"} | awk '{{print $4}}')
sbatch --dependency=afterok:$scheduling_id {self.master_dir / "analyze_results.slurm"}
"""
            )
        print(f"Main master SLURM file written at {slurm_file}")

    def generate_analyze_slurm(self):
        """Generate the SLURM file for analyzing results."""
        print("Generating the SLURM file for analyzing results")
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
{self.modules}

# Exécuter le script d'analyse
python3 {self.main_path}/main.py analyze_results {self.experience_id}
"""
            )
        print(f"SLURM file for analyzing results written at {slurm_file}")

    def generate_all_slurm(self):
        """Generate all the SLURM files for a given experience."""
        print(
            f"Generating all SLURM files for experience ID: {self.experience_id}")

        # Pour chaque type de configuration (taskset, assignment, scheduling)
        for config_type in ["taskset", "assignment", "scheduling"]:
            # Récupérer les IDs de configuration pour ce type
            print(f"Fetching config IDs for {config_type}")
            config_ids = self.experience_loader.get_config_ids(config_type)

            # Gérer les jobs par batch de batch_size
            i = 0
            while i < len(config_ids):
                # Créer un dictionnaire pour le batch actuel
                batch_configs = {}
                for j in range(i, min(i + self.batch_size, len(config_ids))):
                    config_key = config_ids[j]
                    batch_configs[config_key] = config_key

                # Nom du batch actuel
                batch_name = f"batch_{config_type}_{i // self.batch_size}"

                # Générer le script SLURM pour le batch actuel
                print(f"Generating SLURM batch file for {batch_name}")
                slurm_file = self.slurm_dir / config_type / \
                    f"batch/{batch_name}.slurm"
                param_exclude = [f"batch_{config_type}",
                                 f"all_{config_type}s_master"]
                with open(slurm_file, "w") as f:
                    f.write(
                        f"""#!/bin/bash
#SBATCH --job-name={batch_name}
#SBATCH --output={self.output_dir / config_type / f"output_{batch_name}.txt"}
#SBATCH --ntasks=1
#SBATCH --time={self.slurm_parameters.get(f"{config_type}_time", "02:00:00")}
#SBATCH --mem=2G

for config_key in {" ".join(batch_configs.keys())}; do  # Séparer par des espaces
  sbatch {self.slurm_dir / config_type / f"$config_key.slurm"}  # Utiliser le chemin complet
done

{self.get_wait_for_jobs_script(config_type, param_exclude)}
                    """
                    )

                # Générer les fichiers SLURM individuels pour le batch
                for config_key in batch_configs.keys():
                    self.generate_slurm(config_key, config_type)

                i += self.batch_size

        # Générer les fichiers SLURM masters
        self.generate_master_slurm()

        # Générer le fichier SLURM pour l'analyse des résultats
        self.generate_analyze_slurm()
        print("All SLURM files generated successfully")
