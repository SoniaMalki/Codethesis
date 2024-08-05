from pathlib import Path
from datetime import time
import json
import socket
from modules.core.experience_loader import ExperienceLoader


class SlurmGenerator:
    def __init__(self, main_path, generation_path, db_path, experience_id, experience_data, batch_size=100):
        self.main_path = Path(main_path)
        self.generation_path = Path(generation_path)
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
        print(self.db_path)

        for dir_path in [self.master_dir, self.slurm_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.experience_loader = ExperienceLoader(self.db_path)

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
        print(f"hostname: {hostname}")
        # Charger les modules en fonction du cluster
        self.modules = self.get_modules_for_hostname(hostname)
        print(f"self.modules: {self.modules}")

        for config_type in ["taskset", "assignment", "scheduling"]:
            (self.slurm_dir / config_type).mkdir(parents=True, exist_ok=True)
            (self.output_dir / config_type).mkdir(parents=True, exist_ok=True)

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
python3 {self.main_path} / "main.py" {self.experience_key} run_experience {config_key}
"""

    def generate_slurm(self, config_key, config_type):
        """Generate SLURM file for a specific configuration."""
        slurm_file = self.slurm_dir / config_type / f"{config_key}.slurm"
        with open(slurm_file, "w") as f:
            f.write(self.get_slurm_content(config_key, config_type))

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
        slurm_file = self.master_dir / f"all_{config_type}s_master.slurm"

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

            # Récupérer la liste des fichiers SLURM du dossier correspondant
            slurm_files = sorted(
                (self.slurm_dir / config_type).glob("*.slurm")
            )

            # Lancer les fichiers SLURM en séquence avec dépendances
            previous_batch_id_var = None
            for i, slurm_file in enumerate(slurm_files):
                batch_name = slurm_file.stem
                current_batch_id_var = f"{batch_name}_ID"

                if previous_batch_id_var:
                    f.write(
                        f"""{current_batch_id_var}=$(sbatch --dependency=afterok:${previous_batch_id_var} {slurm_file} | awk '{{print $4}}')\n"""
                    )
                else:
                    f.write(
                        f"""{current_batch_id_var}=$(sbatch {slurm_file} | awk '{{print $4}}')\n"""
                    )
                previous_batch_id_var = current_batch_id_var

            f.write(
                f"""
{self.get_wait_for_jobs_script(config_type, f"all_{config_type}s_master")}
"""
            )

    def generate_master_slurm(self):
        """Generate the main master SLURM file."""
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
{self.modules}

# Exécuter le script d'analyse
python3 {self.main_path} / "main.py" {self.experience_id} analyze_results_db
"""
            )

    def generate_all_slurm(self):
        for config_type in ["taskset", "assignment", "scheduling"]:
            # Générer les fichiers SLURM individuels
            config_ids = self.experience_loader.get_config_ids(config_type)
            for config_id in config_ids:
                self.generate_slurm(config_id, config_type)

            # Générer les fichiers SLURM masters
            self.generate_master_slurm()

        # Générer le fichier SLURM pour l'analyse des résultats
        self.generate_analyze_slurm()

    def generate_estimation(self):
        # Define the base path for the estimation files
        estimation_dir = self.main_path / "estimation_slurm"
        estimation_dir.mkdir(parents=True, exist_ok=True)

        # File paths for the slurm scripts
        master_file = estimation_dir / "master.slurm"
        batch_taskset_file = estimation_dir / "batch_taskset.slurm"
        batch_assignment_file = estimation_dir / "batch_assignment.slurm"
        batch_scheduling_file = estimation_dir / "batch_scheduling.slurm"

        # Content for master.slurm
        master_content = """#!/bin/bash
#SBATCH --job-name=master
#SBATCH --output=/home/smalki/Codethesis/estimation_slurm/master.txt
#SBATCH --ntasks=1
#SBATCH --time=00:02:00
#SBATCH --mem=2G

taskset_id=$(sbatch /home/smalki/Codethesis/estimation_slurm/batch_taskset.slurm | awk '{print $4}')
assignment_id=$(sbatch --dependency=afterok:$taskset_id /home/smalki/Codethesis/estimation_slurm/batch_assignment.slurm | awk '{print $4}')
scheduling_id=$(sbatch --dependency=afterok:$assignment_id /home/smalki/Codethesis/estimation_slurm/batch_scheduling.slurm | awk '{print $4}')
"""

        # Content for batch_taskset.slurm
        batch_taskset_content = """#!/bin/bash
#SBATCH --job-name=batch_taskset
#SBATCH --output=/home/smalki/Codethesis/estimation_slurm/batch_taskset.txt
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --mem=2G

# Define experience IDs
exp_ids=(
    "taskset_generate_3_c8"
    "taskset_generate_53_c4"
    "taskset_generate_7_c2"
    "taskset_generate_60_c8"
    "taskset_generate_11_c4"
    "taskset_generate_67_c2"
    "taskset_generate_18_c8"
    "taskset_generate_62_c4"
    "taskset_generate_22_c2"
    "taskset_generate_72_c8"
)

# Execute experiences in sequence
for exp_id in "${exp_ids[@]}"; do
    sbatch /home/smalki/Codethesis/generation/estimation_experience/slurm/slurm_files/taskset/${exp_id}.slurm
done

# Wait for all jobs to finish
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'taskset' | grep -v 'batch_taskset' | wc -l) -gt 0 ]; do
    sleep 1
done
"""

        # Content for batch_assignment.slurm
        batch_assignment_content = """#!/bin/bash
#SBATCH --job-name=batch_assignment
#SBATCH --output=/home/smalki/Codethesis/estimation_slurm/batch_assignment.txt
#SBATCH --ntasks=1
#SBATCH --time=2:00:00
#SBATCH --mem=4G

# Define experience IDs
exp_ids=(
    "assignment_generate_75_c8"
    "assignment_generate_1935_c4"
    "assignment_generate_243_c2"
    "assignment_generate_2214_c8"
    "assignment_generate_407_c4"
    "assignment_generate_2479_c2"
    "assignment_generate_646_c8"
    "assignment_generate_2283_c4"
    "assignment_generate_813_c2"
    "assignment_generate_2664_c8"
)

# Execute experiences in sequence
for exp_id in "${exp_ids[@]}"; do
    sbatch /home/smalki/Codethesis/generation/estimation_experience/slurm/slurm_files/assignment/${exp_id}.slurm
done

# Wait for all jobs to finish
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'assignment' | grep -v 'batch_assignment' | wc -l) -gt 0 ]; do
    sleep 1
done
"""

        # Content for batch_scheduling.slurm
        batch_scheduling_content = """#!/bin/bash
#SBATCH --job-name=batch_scheduling
#SBATCH --output=/home/smalki/Codethesis/estimation_slurm/batch_scheduling.txt
#SBATCH --ntasks=1
#SBATCH --time=4:00:00
#SBATCH --mem=16G

# Define experience IDs
exp_ids=(
    "scheduling_generate_519_c8"
    "scheduling_generate_13543_c4"
    "scheduling_generate_1701_c2"
    "scheduling_generate_15493_c8"
    "scheduling_generate_2846_c4"
    "scheduling_generate_17353_c2"
    "scheduling_generate_4518_c8"
    "scheduling_generate_15979_c4"
    "scheduling_generate_5691_c2"
    "scheduling_generate_18643_c8"
)

# Execute experiences in sequence
for exp_id in "${exp_ids[@]}"; do
    sbatch /home/smalki/Codethesis/generation/estimation_experience/slurm/slurm_files/scheduling/${exp_id}.slurm
done

# Wait for all jobs to finish
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep 'scheduling' | grep -v 'batch_scheduling' | wc -l) -gt 0 ]; do
    sleep 1
done
"""

        # Write the content to files
        with open(master_file, 'w') as f:
            f.write(master_content)
        with open(batch_taskset_file, 'w') as f:
            f.write(batch_taskset_content)
        with open(batch_assignment_file, 'w') as f:
            f.write(batch_assignment_content)
        with open(batch_scheduling_file, 'w') as f:
            f.write(batch_scheduling_content)
