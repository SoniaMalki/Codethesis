import os
import json
import socket
from pathlib import Path
from datetime import time
from time import sleep
import re

from modules.core.experience_loader import ExperienceLoader
from modules.utils.db_utils import DBUtils


class SlurmGenerator:
    def __init__(self, main_path, generation_path, db_path, experience_id, experience_data, batch_size=100):
        print("Initializing SlurmGenerator")
        self.main_path = Path(main_path)
        self.generation_path = Path(generation_path) / experience_id
        self.db_path = db_path
        self.experience_id = experience_id

        # Centralized SLURM Parameters
        self.default_slurm_time = "2-00:00:00"
        self.default_slurm_mem = "2G"
        self.analyze_slurm_time = "01:00:00"
        self.analyze_slurm_mem = "4G"

        # Dictionnaire des paramètres SLURM par défaut
        self.slurm_parameters = {
            "taskset": {"time": "01:00:00", "mem": "1G", "batch_size": 500},
            "assignment_simple": {"time": "00:20:00", "mem": "1G", "batch_size": 5},
            "assignment_milp": {"time": "05:00:00", "mem": "4G", "batch_size": 5},
            "scheduling_simple": {"time": "01:00:00", "mem": "4G", "batch_size": 5},
            "scheduling_combined": {"time": "02:00:00", "mem": "4G", "batch_size": 5},
            "scheduling_rhma": {"time": "05:00:00", "mem": "64G", "batch_size": 5},
        }

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

        self.cluster_cores = {
            "lm": 10,
            "nic": 10,
            "her": 10,
            "sonia": 3
        }

        hostname = socket.gethostname()
        print(f"Hostname: {hostname}")
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

    def get_wait_for_jobs_script(self, job_name, exclude_name):
        if type(exclude_name) != list:
            exclude_name = [exclude_name]

        grep_command = [
            f"| grep -v '{ex_name}'" for ex_name in exclude_name]
        grep_command = ''.join(grep_command)

        return f"""# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep '{job_name}' {grep_command} | wc -l) -gt 0 ]; do
  sleep 15
done
"""

    def get_slurm_content(self, config_key, config_type, optimal_threads, job_time, slurm_memory):

        return f"""#!/bin/bash
#SBATCH --job-name={config_key}
#SBATCH --output={self.output_dir / config_type / f"{config_key}.txt"}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={optimal_threads}
#SBATCH --time={job_time}
#SBATCH --mem={slurm_memory}

# Charger les modules nécessaires
{self.modules}

python3 -u {self.main_path}/main.py run_experience {self.experience_id} {config_key}
"""

    def determine_optimal_resources(self, config_params, config_type):
        hostname = socket.gethostname()
        cluster_name = next(
            (cluster for cluster in self.cluster_cores if cluster in hostname), None
        )

        print(f"Cluster name: {cluster_name}")
        print(f"Algorithm : {config_params.get('assignment_method', '')}")

        if cluster_name is None:
            print(
                f"Warning: Unknown cluster '{hostname}'. Defaulting to 1 core.")
            available_cores = 1
        else:
            available_cores = self.cluster_cores[cluster_name]

        if config_type == "assignment":
            if "Wmin" in config_params.get('assignment_method', "") or "Citta" in config_params.get('assignment_method', ""):
                optimal_cores = min(available_cores, 8)
            else:
                optimal_cores = min(available_cores, 1)
        elif config_type == "scheduling":
            if "Rhma" in config_params.get('scheduling_algorithm', ""):
                optimal_cores = min(available_cores, 8)
            else:
                optimal_cores = 1
        else:
            optimal_cores = 1

        optimal_threads = optimal_cores

        return optimal_threads

    def get_job_time_and_memory(self, config_type, config_params):
        if config_type == "taskset":
            return self.slurm_parameters["taskset"]["time"], self.slurm_parameters["taskset"]["mem"]
        elif config_type == "assignment":
            if "Wmin" in config_params.get('assignment_method', "") or "Citta" in config_params.get('assignment_method', ""):
                return self.slurm_parameters["assignment_milp"]["time"], self.slurm_parameters["assignment_milp"]["mem"]
            else:
                return self.slurm_parameters["assignment_simple"]["time"], self.slurm_parameters["assignment_simple"]["mem"]
        elif config_type == "scheduling":
            if "Rhma" in config_params.get('scheduling_algorithm', ""):
                return self.slurm_parameters["scheduling_rhma"]["time"], self.slurm_parameters["scheduling_rhma"]["mem"]
            elif "Combined" in config_params.get('scheduling_algorithm', ""):
                return self.slurm_parameters["scheduling_combined"]["time"], self.slurm_parameters["scheduling_combined"]["mem"]
            else:
                return self.slurm_parameters["scheduling_simple"]["time"], self.slurm_parameters["scheduling_simple"]["mem"]
        else:
            return "02:00:00", "8G"

    def get_batch_size(self, config_type, algorithm):
        algorithm = algorithm["algorithm"]
        if config_type == "taskset":
            key = "taskset"
        elif config_type == "assignment":
            key = "assignment_milp" if "Wmin" in algorithm or "Citta" in algorithm else "assignment_simple"
        elif config_type == "scheduling":
            key = "scheduling_rhma" if "Rhma" in algorithm else (
                "scheduling_combined" if "Combined" in algorithm else "scheduling_simple"
            )
        else:
            return 100  # Default value

        return self.slurm_parameters[key]["batch_size"]

    def generate_slurm(self, config_key, config_type):
        """Generate SLURM file for a specific configuration."""
        print(f"Generating SLURM file for {config_key} of type {config_type}")

        # Load experience to check if a result file exists and get parameters
        experience = self.experience_loader.load(config_key)

        if experience and not experience.get_result_file_path(config_type):
            if config_type == "assignment":
                config_params = experience.assignment_parameters['parameters']
                optimal_threads = self.determine_optimal_resources(
                    config_params, config_type)
                # Set threads in assignment_options
                config_params['assignment_options']['threads'] = optimal_threads

            elif config_type == "scheduling":
                config_params = experience.scheduling_parameters['parameters']
                optimal_threads = self.determine_optimal_resources(
                    config_params, config_type)
                # Set threads in scheduling_options
                config_params['scheduling_options']['threads'] = optimal_threads

            elif config_type == "taskset":
                config_params = {}  # Assuming no specific parameters for taskset
                optimal_threads = 1  # Default to 1 if no parameters found

            # Get Slurm time and memory based on configuration type
            job_time, slurm_memory = self.get_job_time_and_memory(
                config_type, config_params)

            slurm_file = self.slurm_dir / \
                config_type / f"{config_key}.slurm"

            with open(slurm_file, "w") as f:
                f.write(self.get_slurm_content(
                    config_key, config_type, optimal_threads, job_time, slurm_memory))

            print(f"SLURM file for {config_key} generated at {slurm_file}")

            # Update database with cluster, threads, time, and memory information
            self.update_database_with_slurm_info(
                config_key, config_type, optimal_threads, job_time, slurm_memory)
        else:
            print(
                f"Skipping SLURM generation for {config_key} - result file already exists")

    def update_database_with_slurm_info(self, config_key, config_type, threads, slurm_time, slurm_memory):
        """Updates the Tasksets, Assignments, or Schedulings table with cluster, threads, time limit, and memory."""

        hostname = socket.gethostname()

        cluster_mapping = {
            "lm": "lemaitre4",
            "nic": "nic5",
            "her": "hercules",
            "sonia": "sonia"
        }

        cluster_name = next((value for key, value in cluster_mapping.items(
        ) if hostname.startswith(key)), hostname)

        db_utils = DBUtils(self.db_path)  # Create DBUtils instance
        if config_type == "assignment":
            table_name = "Assignments"
            id_column = "assignment_id"
        elif config_type == "scheduling":
            table_name = "Schedulings"
            id_column = "scheduling_id"
        elif config_type == "taskset":
            table_name = "Tasksets"
            id_column = "taskset_id"
        else:
            print(f"Error: Invalid config_type: {config_type}")
            return

        try:
            # Use db_utils.cursor here to execute the SQL command
            db_utils.cursor.execute(f"""
                UPDATE {table_name}
                SET cluster = ?,
                    threads = ?,
                    slurm_time = ?,
                    slurm_memory = ?
                WHERE {id_column} = ?
            """, (cluster_name, threads, slurm_time, slurm_memory, config_key))
            db_utils.conn.commit()  # Commit using the DBUtils connection
            print(
                f"Updated {table_name} table with Slurm info for {config_key}")
        except Exception as e:
            print(f"Error updating {table_name} table: {e}")

    def generate_analyze_slurm(self):
        print("Generating the SLURM file for analyzing results")
        slurm_file = self.master_dir / "analyze_results.slurm"
        with open(slurm_file, "w") as f:
            f.write(
                f"""#!/bin/bash
#SBATCH --job-name=analyze_results
#SBATCH --output={self.output_dir / f"analyze_results.txt"}
#SBATCH --ntasks=1
#SBATCH --time={self.analyze_slurm_time}
#SBATCH --mem={self.analyze_slurm_mem}

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

            # 1. Generate Individual SLURM Files (if needed)
            for config_key in config_ids:
                self.generate_slurm(config_key, config_type)

            # 2. Read Individual SLURM Directory
            individual_slurm_dir = self.slurm_dir / config_type
            generated_slurm_files = list(individual_slurm_dir.glob("*.slurm"))

            # 3. Construct Batch Files
            i = 0

            # Regroupement des fichiers SLURM par type de configuration
            grouped_slurm_files = {}
            for slurm_file in generated_slurm_files:
                config_key = slurm_file.stem
                experience = self.experience_loader.load(config_key)
                if experience:
                    if config_type == "assignment":
                        config_params = experience.assignment_parameters['parameters']
                        algorithm = config_params.get(
                            'assignment_method', 'simple')
                    elif config_type == "scheduling":
                        config_params = experience.scheduling_parameters['parameters']
                        algorithm = config_params.get(
                            'scheduling_algorithm', 'simple')
                    else:
                        algorithm = "taskset"  # Default for taskset

                    if algorithm not in grouped_slurm_files:
                        grouped_slurm_files[algorithm] = []
                    grouped_slurm_files[algorithm].append(slurm_file)

            # Création des fichiers batch pour chaque groupe
            for algorithm, slurm_files in grouped_slurm_files.items():
                i = 0

                batch_size = self.get_batch_size(
                    config_type, {"algorithm": algorithm})

                # --- Use enumerate for batch naming ---
                for batch_num, _ in enumerate(range(0, len(slurm_files), batch_size)):
                    batch_configs = {}
                    for j in range(i, min(i + batch_size, len(slurm_files))):
                        slurm_file = slurm_files[j]
                        config_key = slurm_file.stem
                        batch_configs[config_key] = config_key

                    # Nom du batch actuel
                    # Use batch_num for name
                    batch_name = f"batch_{config_type}_{algorithm}_{batch_num}"

                    # --- Sort batch_configs numerically (CORRECTED) ---
                    sorted_batch_configs = dict(
                        sorted(batch_configs.items(), key=lambda item: int(item[0].split('_')[1])))

                    print(f"Generating SLURM batch file for {batch_name}")
                    slurm_file = self.slurm_dir / \
                        config_type / f"batch/{batch_name}.slurm"
                    param_exclude = [
                        f"batch_{config_type}", f"all_{config_type}s_master"]
                    with open(slurm_file, "w") as f:
                        f.write(
                            f"""#!/bin/bash
#SBATCH --job-name={batch_name}
#SBATCH --output={self.output_dir / config_type / f"{batch_name}.txt"}
#SBATCH --ntasks=1
#SBATCH --time={self.default_slurm_time}
#SBATCH --mem={self.default_slurm_mem}

# Séparer par des espaces
# Use sorted_batch_configs
for config_key in {" ".join(sorted_batch_configs.keys())}; do
  # Utiliser le chemin complet
  sbatch {individual_slurm_dir / f"$config_key.slurm"}
done

{self.get_wait_for_jobs_script(config_type, param_exclude)}
                            """
                        )

                    i += batch_size
        # 4 & 5. Construct Master Files (per type)
        for config_type in ["taskset", "assignment", "scheduling"]:
            self.write_master_slurm(config_type)

        # Générer le fichier SLURM pour l'analyse des résultats
        self.generate_analyze_slurm()
        print("All SLURM files generated successfully")

    def write_master_slurm(self, config_type):
        """Write master SLURM file for a configuration type."""
        print(f"Writing master SLURM file for {config_type}")
        slurm_file = self.master_dir / f"all_{config_type}s_master.slurm"
        batch_files = sorted(
            (self.slurm_dir / config_type / "batch").glob("*.slurm"),
            key=lambda x: self.extract_batch_number(x.name)
        )
        # Only write the master file if there are batch files
        if batch_files:
            with open(slurm_file, "w") as f:
                f.write(
                    f"""#!/bin/bash
#SBATCH --job-name=all_{config_type}s_master
#SBATCH --output={self.output_dir / config_type / f"{config_type}s_master.txt"}
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
        {self.get_wait_for_jobs_script(
            config_type, f"all_{config_type}s_master")}
        """
                )
            print(
                f"Master SLURM file for {config_type} written at {slurm_file}")
        else:
            print(
                f"Skipping master SLURM generation for {config_type} - No batch files found")

    # Add this method to your class:
    def extract_batch_number(self, filename):
        match = re.search(r'batch_[^_]+_(\d+)', filename)
        if match:
            return int(match.group(1))
        else:
            print(
                f"Warning: No batch number found in {filename}. Defaulting to 0.")
            return 0
