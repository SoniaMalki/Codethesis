import socket
from pathlib import Path
import re
import io
from collections import defaultdict

from modules.utils.db_utils import DBUtils


class SlurmGenerator:
    def __init__(self, main_path, generation_path, db_path, experience_id, experience_data, batch_size=100):
        print("Initializing SlurmGenerator")
        self.main_path = Path(main_path)
        self.generation_path = Path(generation_path) / experience_id
        self.db_path = db_path
        self.experience_id = experience_id

        # Define priority lists
        self.assignment_algorithm_priority = [
            "WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner", "Wmin", "Citta"]
        self.scheduling_algorithm_priority = ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1", "EarliestDeadlineFirstVariant2",
                                              "DeadlineMonotonic", "DeadlineMonotonicVariant1", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]

        # Centralized SLURM Parameters
        self.default_slurm_time = "2-00:00:00"
        self.default_slurm_mem = "1G"
        self.analyze_slurm_time = "2-00:00:00"
        self.analyze_slurm_mem = "4G"
        self.master_slurm_time = "2-00:00:00"
        self.master_slurm_mem = "100M"
        self.batch_slurm_time = "2-00:00:00"
        self.batch_slurm_mem = "100M"
        self.full_pipeline_time = "2-00:00:00"
        self.full_pipeline_mem = "500M"
        self.default_batch_size = batch_size

        # Dictionnaire des paramètres SLURM par défaut
        self.slurm_parameters = {
            "taskset": {"time": "01:00:00", "mem": "200M", "batch_size": 400},
            "assignment_simple": {"time": "00:20:00", "mem": "1G", "batch_size": 400},
            "assignment_milp": {"time": "05:00:00", "mem": "1G", "batch_size": 200},
            "scheduling_simple": {"time": "01:00:00", "mem": "1G", "batch_size": 400},
            "scheduling_combined": {"time": "02:00:00", "mem": "1G", "batch_size": 200},
            "scheduling_rhma": {"time": "05:00:00", "mem": "32G", "batch_size": 400},
        }

        self.master_dir = self.generation_path / "slurm" / "master"
        self.slurm_dir = self.generation_path / "slurm" / "slurm_files"
        self.output_dir = self.generation_path / "slurm" / "output"
        print(f"DB path: {self.db_path}")

        for dir_path in [self.master_dir, self.slurm_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

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
#SBATCH --exclude=her2-w120
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
            "drg2": """
module load Python/3.11.3-GCCcore-12.3.0
export GLOBALSCRATCH=$HOME
""",
        }

        self.cluster_cores = {
            "lm": 10,
            "nic": 10,
            "her": 10,
            "drg2": 10,
            "sonia": 3
        }

        hostname = socket.gethostname()
        print(f"Hostname: {hostname}")
        self.modules = self.get_modules_for_hostname(hostname)
        print(f"Loaded modules: {self.modules}")

        # Pre-calculate cluster resources for faster access using defaultdict
        self.cluster_resources = defaultdict(lambda: {
            "optimal_threads": self.determine_optimal_resources("scheduling", "simple"),
            "job_time": self.get_job_time_and_memory("scheduling", "simple")[0],
            "slurm_memory": self.get_job_time_and_memory("scheduling", "simple")[1],
            "batch_size": self.get_batch_size("scheduling", "simple")
        })
        for config_type in ["taskset", "assignment", "scheduling"]:
            for algorithm in (self.assignment_algorithm_priority if config_type == "assignment" else
                              self.scheduling_algorithm_priority if config_type == "scheduling" else
                              ["taskset"]):
                self.cluster_resources[(config_type, algorithm)] = {
                    "optimal_threads": self.determine_optimal_resources(config_type, algorithm),
                    "job_time": self.get_job_time_and_memory(config_type, algorithm)[0],
                    "slurm_memory": self.get_job_time_and_memory(config_type, algorithm)[1],
                    "batch_size": self.get_batch_size(config_type, algorithm)
                }

        # No longer need explicit entries for None algorithm

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
#SBATCH --mem-per-cpu={slurm_memory}
{self.modules}
source $GLOBALSCRATCH/myenv/bin/activate
python3 -u {self.main_path}/main.py run_experience {self.experience_id} {config_key}
"""

    def determine_optimal_resources(self, config_type, algorithm):
        hostname = socket.gethostname()
        cluster_name = next(
            (cluster for cluster in self.cluster_cores if cluster in hostname), None
        )

        print(f"Cluster name: {cluster_name}")
        print(f"Algorithm : {algorithm}")

        if cluster_name is None:
            print(
                f"Warning: Unknown cluster '{hostname}'. Defaulting to 1 core.")
            available_cores = 1
        else:
            available_cores = self.cluster_cores[cluster_name]

        if config_type == "assignment":
            if "Wmin" in algorithm or "Citta" in algorithm:
                optimal_cores = min(available_cores, 8)
            else:
                optimal_cores = min(available_cores, 1)
        elif config_type == "scheduling":
            if "Rhma" in algorithm:
                optimal_cores = min(available_cores, 8)
            else:
                optimal_cores = 1
        else:
            optimal_cores = 1

        optimal_threads = optimal_cores
        return optimal_threads

    def get_job_time_and_memory(self, config_type, algorithm):
        if config_type == "taskset":
            return self.slurm_parameters["taskset"]["time"], self.slurm_parameters["taskset"]["mem"]
        elif config_type == "assignment":
            if "Wmin" in algorithm or "Citta" in algorithm:
                return self.slurm_parameters["assignment_milp"]["time"], self.slurm_parameters["assignment_milp"]["mem"]
            else:
                return self.slurm_parameters["assignment_simple"]["time"], self.slurm_parameters["assignment_simple"]["mem"]
        elif config_type == "scheduling":
            if "Rhma" in algorithm:
                return self.slurm_parameters["scheduling_rhma"]["time"], self.slurm_parameters["scheduling_rhma"]["mem"]
            elif "Combined" in algorithm:
                return self.slurm_parameters["scheduling_combined"]["time"], self.slurm_parameters["scheduling_combined"]["mem"]
            else:
                return self.slurm_parameters["scheduling_simple"]["time"], self.slurm_parameters["scheduling_simple"]["mem"]
        else:
            return self.default_slurm_time, self.default_slurm_mem

    def get_batch_size(self, config_type, algorithm):
        if config_type == "taskset":
            key = "taskset"
        elif config_type == "assignment":
            key = "assignment_milp" if "Wmin" in algorithm or "Citta" in algorithm else "assignment_simple"
        elif config_type == "scheduling":
            key = "scheduling_rhma" if "Rhma" in algorithm else (
                "scheduling_combined" if "Combined" in algorithm else "scheduling_simple"
            )
        else:
            return self.default_batch_size

        return self.slurm_parameters[key]["batch_size"]

    def generate_slurm_batch(self, config_type, algorithm, batch_configs, batch_num):
        individual_slurm_dir = self.slurm_dir / config_type
        batch_name = f"batch_{config_type}_{algorithm}_{batch_num}"

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
#SBATCH --time={self.batch_slurm_time}
#SBATCH --mem-per-cpu={self.batch_slurm_mem}
{self.modules}

# Définir la liste des configurations
configs=(\n""")
            for config_key in sorted_batch_configs.keys():
                f.write(f"  {config_key}\n")

            f.write(
                f""")

# Boucle sur la liste des configurations
for config_key in "${{configs[@]}}"; do
  tempfile=$(mktemp /tmp/slurm_batch_XXXXXX)
  sbatch {individual_slurm_dir}/$config_key.slurm >"$tempfile" 2>&1
  output=$(cat "$tempfile")
  if echo "$output" | grep -q "error"; then
    echo "Job not launched. Output: $output"
  else
    job_id=$(echo "$output" | awk '{{print $4}}')
    job_name=$(scontrol show job "$job_id" | grep "JobName=" | awk -F= '{{print $3}}')
    echo "$output | Job Name: $job_name | Job ID : $job_id"
  fi
  rm -f "$tempfile"
done

{self.get_wait_for_jobs_script(config_type, param_exclude)}
                            """
            )

    def generate_slurm_for_config(self, config_key, config_type, algorithm):
        """Generate SLURM file for a specific configuration, only if result file does not exist."""
        print(
            f"Generating SLURM file for {config_key} of type {config_type} with algo {algorithm}")

        with DBUtils(self.db_path, self.assignment_algorithm_priority, self.scheduling_algorithm_priority) as db_utils:
            if config_type == "assignment":
                result_exists = db_utils.check_result_exists(
                    "Assignments", "assignment_id", config_key)
            elif config_type == "scheduling":
                result_exists = db_utils.check_result_exists(
                    "Schedulings", "scheduling_id", config_key)
            elif config_type == "taskset":
                result_exists = db_utils.check_result_exists(
                    "Tasksets", "taskset_id", config_key)
            else:
                print(
                    f"Error: Invalid config_type: {config_type}")
                return

            if not result_exists:
                resources = self.cluster_resources[(config_type, algorithm)]
                optimal_threads = resources["optimal_threads"]
                job_time = resources["job_time"]
                slurm_memory = resources["slurm_memory"]

                # Use StringIO for in-memory buffering
                slurm_content = io.StringIO()
                slurm_content.write(self.get_slurm_content(
                    config_key, config_type, optimal_threads, job_time, slurm_memory))

                slurm_file = self.slurm_dir / \
                    config_type / f"{config_key}.slurm"

                # Write the entire content to disk
                with open(slurm_file, "w") as f:
                    f.write(slurm_content.getvalue())

                print(
                    f"SLURM file for {config_key} generated at {slurm_file}")

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
            "drg2": "dragon2",
            "sonia": "sonia"
        }

        cluster_name = next((value for key, value in cluster_mapping.items(
        ) if hostname.startswith(key)), hostname)

        with DBUtils(self.db_path, self.assignment_algorithm_priority, self.scheduling_algorithm_priority) as db_utils:
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
                db_utils.cursor.execute(f"""
                    UPDATE {table_name}
                    SET cluster = ?,
                        threads = ?,
                        slurm_time = ?,
                        slurm_memory = ?
                    WHERE {id_column} = ?
                """, (cluster_name, threads, slurm_time, slurm_memory, config_key))
                db_utils.conn.commit()

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
#SBATCH --mem-per-cpu={self.analyze_slurm_mem}
{self.modules}

# Exécuter le script d'analyse
source $GLOBALSCRATCH/myenv/bin/activate
python3 -u {self.main_path}/main.py analyze_results {self.experience_id}
"""
            )
        print(f"SLURM file for analyzing results written at {slurm_file}")

    def generate_all_slurm(self):
        """Generate all the SLURM files for a given experience."""
        print(
            f"Generating all SLURM files for experience ID: {self.experience_id}")

        for config_type in ["taskset", "assignment", "scheduling"]:
            print(f"Fetching config IDs for {config_type}")
            slurm_data_to_update = []

            # Determine cluster_name here, outside the if block
            hostname = socket.gethostname()
            cluster_mapping = {
                "lm": "lemaitre4",
                "nic": "nic5",
                "her": "hercules",
                "sonia": "sonia"
            }
            cluster_name = next((value for key, value in cluster_mapping.items(
            ) if hostname.startswith(key)), hostname)

            with DBUtils(self.db_path, self.assignment_algorithm_priority, self.scheduling_algorithm_priority) as db_utils:
                if config_type == 'taskset':
                    grouped_config_ids = db_utils.get_config_ids_with_no_results(
                        "Tasksets", "taskset_id", self.experience_id)
                elif config_type == 'assignment':
                    grouped_config_ids = db_utils.get_config_ids_with_no_results(
                        "Assignments", "assignment_id", self.experience_id)
                elif config_type == 'scheduling':
                    grouped_config_ids = db_utils.get_config_ids_with_no_results(
                        "Schedulings", "scheduling_id", self.experience_id)
                else:
                    print(f"Error: Invalid config_type: {config_type}")
                    continue

                # 1 & 2. Generate SLURM Files and Group Batches
                grouped_slurm_files = {}
                for algorithm, config_ids in grouped_config_ids.items():
                    for config_key in config_ids:
                        resources = self.cluster_resources[(
                            config_type, algorithm)]
                        optimal_threads = resources["optimal_threads"]
                        job_time = resources["job_time"]
                        slurm_memory = resources["slurm_memory"]

                        self.generate_slurm_for_config(
                            config_key, config_type, algorithm)

                        # Accumulate data for bulk update
                        slurm_data_to_update.append(
                            (cluster_name, optimal_threads,
                             job_time, slurm_memory, config_key)
                        )

                        if algorithm not in grouped_slurm_files:
                            grouped_slurm_files[algorithm] = {}
                        grouped_slurm_files[algorithm][config_key] = config_key

                # 3. Construct Batch Files
                for algorithm, batch_configs in grouped_slurm_files.items():
                    batch_size = self.cluster_resources[(
                        config_type, algorithm)]["batch_size"]
                    for batch_num, _ in enumerate(range(0, len(batch_configs), batch_size)):
                        self.generate_slurm_batch(config_type, algorithm, dict(list(batch_configs.items())[
                            batch_num * batch_size:(batch_num + 1) * batch_size]), batch_num)

                # Batch update the database after generating all SLURM files
                if slurm_data_to_update:
                    if config_type == "assignment":
                        table_name = "Assignments"
                        id_column = "assignment_id"
                    elif config_type == "scheduling":
                        table_name = "Schedulings"
                        id_column = "scheduling_id"
                    elif config_type == "taskset":
                        table_name = "Tasksets"
                        id_column = "taskset_id"

                    db_utils.cursor.executemany(f"""
                        UPDATE {table_name}
                        SET cluster = ?,
                            threads = ?,
                            slurm_time = ?,
                            slurm_memory = ?
                        WHERE {id_column} = ?
                    """, slurm_data_to_update)
                    db_utils.conn.commit()

        # 4 & 5. Construct Master Files (per type)
        for config_type in ["taskset", "assignment", "scheduling"]:
            self.write_master_slurm(config_type)

        # Générer le fichier SLURM pour l'analyse des résultats
        self.generate_analyze_slurm()
        print("All SLURM files generated successfully")

    def write_master_slurm(self, config_type):
        """Write master SLURM file for a configuration type."""
        print(f"Writing master SLURM file for {config_type}")

        # Path to the batch files
        batch_dir = self.slurm_dir / config_type / "batch"
        batch_files = list(batch_dir.glob("*.slurm"))

        # Retrieve the priority list based on the configuration type
        if config_type == "assignment":
            priority_list = self.assignment_algorithm_priority
        elif config_type == "scheduling":
            priority_list = self.scheduling_algorithm_priority
        else:
            # Default for taskset, not used as per your use case
            priority_list = ["taskset"]

        # Function to extract priority and numeric suffix from filename
        def extract_priority_and_number(filename):
            base_name = filename.stem
            parts = base_name.split('_')
            priority_rank = priority_list.index(
                parts[2]) if parts[2] in priority_list else len(priority_list)
            numeric_suffix = int(
                parts[-1]) if parts[-1].isdigit() else float('inf')
            return (priority_rank, numeric_suffix)

        # Sorting batch files by priority and then numerically
        sorted_batch_files = sorted(
            batch_files, key=extract_priority_and_number)

        # Master SLURM file path
        slurm_file = self.master_dir / f"all_{config_type}s_master.slurm"

        # Write the master file if there are batch files
        if sorted_batch_files:
            with open(slurm_file, "w") as f:
                f.write(
                    f"""#!/bin/bash
#SBATCH --job-name=all_{config_type}s_master
#SBATCH --output={self.output_dir / config_type / f"{config_type}s_master.txt"}
#SBATCH --ntasks=1
#SBATCH --time={self.master_slurm_time}
#SBATCH --mem-per-cpu={self.master_slurm_mem}
{self.modules}
"""
                )

                # Lancer les batchs avec dépendances
                previous_batch_id_var = None
                for batch_file in sorted_batch_files:
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

    def extract_batch_number(self, filename):
        match = re.search(r'batch_[^_]+_(\d+)', filename)
        if match:
            return int(match.group(1))
        else:
            print(
                f"Warning: No batch number found in {filename}. Defaulting to 0.")
            return 0

    def generate_full_pipeline_slurm(self):
        """Generate the full pipeline SLURM script."""
        print("Generating full pipeline SLURM script")

        command = (
            f"echo \"Starting full pipeline for {self.experience_id}\"\n"
            f"{self.modules}"
            f"source $GLOBALSCRATCH/myenv/bin/activate\n"
            f"python3 -u {self.main_path}/main.py generate_configs {self.experience_id}\n"
            "if [ $? -ne 0 ]; then\n"
            "    echo \"Échec de la génération des configurations\"\n"
            "    exit 1\n"
            "fi\n\n"
            "echo \"Génération des configurations réussie\"\n"
            f"python3 -u {self.main_path}/main.py generate_slurm_files {self.experience_id}\n"
            "if [ $? -ne 0 ]; then\n"
            "    echo \"Échec de la génération des fichiers SLURM\"\n"
            "    exit 1\n"
            "fi\n\n"
            "echo \"Génération des fichiers SLURM réussie\"\n"
            "echo \"Starting master job\"\n"

            # Taskset Submission
            "tempfile=$(mktemp)\n"
            "if [ -f \"$MASTER_DIR/all_tasksets_master.slurm\" ]; then\n"
            "  echo \"Submitting all_tasksets_master.slurm\"\n"
            "  sbatch \"$MASTER_DIR/all_tasksets_master.slurm\" >\"$tempfile\" 2>&1\n"
            "  output=$(cat \"$tempfile\")\n"
            "  if echo \"$output\" | grep -q \"error\"; then\n"
            "    echo \"Job not launched. Output: $output\"\n"
            "  else\n"
            "    taskset_id=$(echo \"$output\" | awk '{print $4}')\n"
            "    job_name=$(scontrol show job $taskset_id | grep \"JobName=\" | awk -F= '{print $3}')\n"
            "    echo \"$output | Job Name: $job_name | Job ID : $taskset_id\"\n"
            "  fi\n"
            "fi\n"
            "rm -f \"$tempfile\"\n"

            # Assignment Submission (dependent on taskset)
            "tempfile=$(mktemp)\n"
            "if [ -f \"$MASTER_DIR/all_assignments_master.slurm\" ]; then\n"
            "  echo \"Submitting all_assignments_master.slurm\"\n"
            "  if [[ -z \"$taskset_id\" ]]; then\n"
            "    sbatch \"$MASTER_DIR/all_assignments_master.slurm\" >\"$tempfile\" 2>&1\n"
            "  else\n"
            "    sbatch --dependency=afterok:$taskset_id \"$MASTER_DIR/all_assignments_master.slurm\" >\"$tempfile\" 2>&1\n"
            "  fi\n"
            "  output=$(cat \"$tempfile\")\n"
            "  if echo \"$output\" | grep -q \"error\"; then\n"
            "    echo \"Job not launched. Output: $output\"\n"
            "  else\n"
            "    assignment_id=$(echo \"$output\" | awk '{print $4}')\n"
            "    job_name=$(scontrol show job $assignment_id | grep \"JobName=\" | awk -F= '{print $3}')\n"
            "    echo \"$output | Job Name: $job_name | Job ID : $assignment_id\"\n"
            "  fi\n"
            "fi\n"
            "rm -f \"$tempfile\"\n"

            # Scheduling Submission (dependent on assignment OR taskset if assignment failed)
            "tempfile=$(mktemp)\n"
            "if [ -f \"$MASTER_DIR/all_schedulings_master.slurm\" ]; then\n"
            "  echo \"Submitting all_schedulings_master.slurm\"\n"
            "  if [[ -z \"$assignment_id\" && -n \"$taskset_id\" ]]; then\n"
            "    sbatch --dependency=afterok:$taskset_id \"$MASTER_DIR/all_schedulings_master.slurm\" >\"$tempfile\" 2>&1\n"
            "  elif [[ -n \"$assignment_id\" ]]; then\n"
            "    sbatch --dependency=afterok:$assignment_id \"$MASTER_DIR/all_schedulings_master.slurm\" >\"$tempfile\" 2>&1\n"
            "  else\n"
            "    sbatch \"$MASTER_DIR/all_schedulings_master.slurm\" >\"$tempfile\" 2>&1\n"
            "  fi\n"
            "  output=$(cat \"$tempfile\")\n"
            "  if echo \"$output\" | grep -q \"error\"; then\n"
            "    echo \"Job not launched. Output: $output\"\n"
            "  else\n"
            "    scheduling_id=$(echo \"$output\" | awk '{print $4}')\n"
            "    job_name=$(scontrol show job $scheduling_id | grep \"JobName=\" | awk -F= '{print $3}')\n"
            "    echo \"$output | Job Name: $job_name | Job ID : $scheduling_id\"\n"
            "  fi\n"
            "fi\n"
            "rm -f \"$tempfile\"\n"

            # Analyze Submission (Conditional)
            "if [[ -n \"$scheduling_id\" ]] || [[ -n \"$assignment_id\" ]]; then\n"
            "  tempfile=$(mktemp)\n"
            "  if [[ -n \"$scheduling_id\" ]]; then\n"
            "    sbatch --dependency=afterok:$scheduling_id \"$MASTER_DIR/analyze_results.slurm\" >\"$tempfile\" 2>&1\n"
            "  elif [[ -n \"$assignment_id\" ]]; then\n"
            "    sbatch --dependency=afterok:$assignment_id \"$MASTER_DIR/analyze_results.slurm\" >\"$tempfile\" 2>&1\n"
            "  fi\n"
            "  output=$(cat \"$tempfile\")\n"
            "  if echo \"$output\" | grep -q \"error\"; then\n"
            "    echo \"Job not launched. Output: echo $output\"\n"
            "  else\n"
            "    analyze_id=$(echo \"$output\" | awk '{print $4}')\n"
            "    job_name=$(scontrol show job $analyze_id | grep \"JobName=\" | awk -F= '{print $3}')\n"
            "    echo \"$output | Job Name: $job_name | Job ID : $analyze_id\"\n"
            "  fi\n"
            "  rm -f \"$tempfile\"\n"
            "fi\n"

            f"echo \"Full pipeline completed for {self.experience_id}\"\n"
        )

        # Create the full_pipeline SLURM script in the master directory
        slurm_file = self.master_dir / \
            f"full_pipeline_{self.experience_id}.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=full_pipeline_{self.experience_id}
#SBATCH --output={self.output_dir / f"full_pipeline_{self.experience_id}.txt"}
#SBATCH --ntasks=1
#SBATCH --time={self.full_pipeline_time}
#SBATCH --mem-per-cpu={self.full_pipeline_mem}
{self.modules}

MASTER_DIR="{self.master_dir}"

{command}
""")

        print(f"Full pipeline SLURM script generated at: {slurm_file}")
