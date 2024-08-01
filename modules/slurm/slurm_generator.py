from pathlib import Path


class SlurmGenerator:
    def __init__(self, main_dir, generation_dir, experience_key, slurm_dir="slurm", output_dir="output"):
        self.main_dir = Path(main_dir)
        self.generation_dir = Path(generation_dir)
        self.experience_key = experience_key

        self.master_dir = self.generation_dir / slurm_dir / "master"
        self.slurm_dir = self.generation_dir / slurm_dir / "slurm_files"
        self.output_dir = self.generation_dir / slurm_dir / output_dir

        self.master_dir.mkdir(parents=True, exist_ok=True)
        self.slurm_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for config_type in ["taskset", "assignment", "scheduling"]:
            (self.slurm_dir / config_type).mkdir(parents=True, exist_ok=True)
            (self.output_dir / config_type).mkdir(parents=True, exist_ok=True)

    def generate_taskset_slurm(self, config_key):
        slurm_file = self.slurm_dir / "taskset" / f"{config_key}.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name={config_key}
#SBATCH --output={self.output_dir / "taskset" / f"output_{config_key}_%j.txt"}
#SBATCH --ntasks=4
#SBATCH --time=02:00:00
#SBATCH --mem=8G

# Charger les modules nécessaires
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0
module load GLPK/5.0-GCCcore-12.3.0
module load tis/2018.01
module load gurobi/gurobi1102

# Exécuter main.py avec la clé d'expérience en argument
python3 {self.main_dir / "main.py"} {self.experience_key} run_experience {config_key}
""")

    def generate_assignment_slurm(self, config_key):
        slurm_file = self.slurm_dir / "assignment" / f"{config_key}.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name={config_key}
#SBATCH --output={self.output_dir / "assignment" / f"output_{config_key}_%j.txt"}
#SBATCH --ntasks=4
#SBATCH --time=02:00:00
#SBATCH --mem=8G

# Charger les modules nécessaires
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0
module load GLPK/5.0-GCCcore-12.3.0
module load tis/2018.01
module load gurobi/gurobi1102


# Exécuter main.py avec la clé d'expérience en argument
python3 {self.main_dir / "main.py"} {self.experience_key} run_experience {config_key}
""")

    def generate_scheduling_slurm(self, config_key):
        slurm_file = self.slurm_dir / "scheduling" / f"{config_key}.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name={config_key}
#SBATCH --output={self.output_dir / "scheduling" / f"output_{config_key}_%j.txt"}
#SBATCH --ntasks=4 
#SBATCH --time=02:00:00 
#SBATCH --mem=8G

# Charger les modules nécessaires
module load releases/2023a
module load Python/3.11.3-GCCcore-12.3.0
module load GLPK/5.0-GCCcore-12.3.0
module load tis/2018.01
module load gurobi/gurobi1102

# Exécuter main.py avec la clé d'expérience en argument
python3 {self.main_dir / "main.py"} {self.experience_key} run_experience {config_key}
""")

    def generate_wait_for_jobs_script(self, job_name, exclude_name):
        return f"""# Attendre que tous les jobs soient terminés
while [ $(squeue -u $USER -h -t RUNNING,PENDING -o "%A %j" | grep '{job_name}' | grep -v '{exclude_name}' | wc -l) -gt 0 ]; do
  sleep 1
done
"""

    def generate_taskset_master_slurm(self):
        slurm_file = self.master_dir / "all_tasksets.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=all_tasksets
#SBATCH --output={self.output_dir / "taskset" / "output_all_tasksets_%j.txt"}
#SBATCH --ntasks=1
#SBATCH --time=04:00:00
#SBATCH --mem=2G

for slurm_file in {self.slurm_dir / "taskset"}/*.slurm; do
  sbatch "$slurm_file"
done

{self.generate_wait_for_jobs_script("taskset", "all_tasksets")}
""")

    def generate_assignment_master_slurm(self):
        slurm_file = self.master_dir / "all_assignments.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=all_assignments
#SBATCH --output={self.output_dir / "assignment" / "output_all_assignments_%j.txt"}
#SBATCH --ntasks=1
#SBATCH --time=04:00:00
#SBATCH --mem=2G 

for slurm_file in {self.slurm_dir / "assignment"}/*.slurm; do
  sbatch "$slurm_file"
done

{self.generate_wait_for_jobs_script("assignment", "all_assignments")}
""")

    def generate_scheduling_master_slurm(self):
        slurm_file = self.master_dir / "all_schedulings.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=all_schedulings
#SBATCH --output={self.output_dir / "scheduling" / "output_all_schedulings_%j.txt"}
#SBATCH --ntasks=1
#SBATCH --time=04:00:00  
#SBATCH --mem=2G  

for slurm_file in {self.slurm_dir / "scheduling"}/*.slurm; do
  sbatch "$slurm_file"
done

{self.generate_wait_for_jobs_script("scheduling", "all_schedulings")}
""")

    def generate_master_slurm(self):
        slurm_file = self.master_dir / "master.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=master_job
#SBATCH --output={self.output_dir / f"master_job_%j.txt"}
#SBATCH --ntasks=1
#SBATCH --time=12:00:00  
#SBATCH --mem=2G 

taskset_id=$(sbatch {self.master_dir / "all_tasksets.slurm"} | awk '{{print $4}}')
assignment_id=$(sbatch --dependency=afterok:$taskset_id {self.master_dir / "all_assignments.slurm"} | awk '{{print $4}}')
sbatch --dependency=afterok:$assignment_id {self.master_dir / "all_schedulings.slurm"}
""")
