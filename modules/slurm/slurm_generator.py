from pathlib import Path


class SlurmGenerator:
    def __init__(self, base_dir, slurm_dir="slurm", output_dir="output"):
        self.base_dir = Path(base_dir)
        self.slurm_dir = self.base_dir / slurm_dir / "slurm_files"
        self.output_dir = self.base_dir / slurm_dir / output_dir

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

# Configurer la licence Gurobi
export GRB_LICENSE_FILE=/home/ulb/parts/smalki/gurobi_keys/gurobi.lic

# Exécuter main.py avec la clé d'expérience en argument
python3 {self.base_dir / "main.py"} run_experience {config_key}
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

# Configurer la licence Gurobi
export GRB_LICENSE_FILE=/home/ulb/parts/smalki/gurobi_keys/gurobi.lic

# Exécuter main.py avec la clé d'expérience en argument
python3 {self.base_dir / "main.py"} run_experience {config_key}
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

# Configurer la licence Gurobi
export GRB_LICENSE_FILE=/home/ulb/parts/smalki/gurobi_keys/gurobi.lic

# Exécuter main.py avec la clé d'expérience en argument
python3 {self.base_dir / "main.py"} run_experience {config_key}
""")

    def generate_taskset_master_slurm(self):
        slurm_file = self.slurm_dir / "taskset" / "all_tasksets.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=all_tasksets
#SBATCH --output={self.output_dir / "taskset" / "output_all_tasksets_%j.txt"}
#SBATCH --ntasks=1
#SBATCH --time=04:00:00
#SBATCH --mem=2G

slurm_dir=$1

# Soumettre tous les jobs de taskset
for slurm_file in "$slurm_dir"/slurm_files/taskset/*.slurm; do
  sbatch "$slurm_file"
done
""")

    def generate_assignment_master_slurm(self):
        slurm_file = self.slurm_dir / "assignment" / "all_assignments.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=all_assignments
#SBATCH --output={self.output_dir / "assignment" / "output_all_assignments_%j.txt"}
#SBATCH --dependency=afterok:all_tasksets
#SBATCH --ntasks=1
#SBATCH --time=04:00:00
#SBATCH --mem=2G 

slurm_dir=$1

for slurm_file in "$slurm_dir"/slurm_files/assignment/*.slurm; do
  sbatch "$slurm_file"
done
""")

    def generate_scheduling_master_slurm(self):
        slurm_file = self.slurm_dir / "scheduling" / "all_schedulings.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=all_schedulings
#SBATCH --output={self.output_dir / "scheduling" / "output_all_schedulings_%j.txt"}
#SBATCH --dependency=afterok:all_assignments
#SBATCH --ntasks=1
#SBATCH --time=04:00:00  
#SBATCH --mem=2G  

slurm_dir=$1

for slurm_file in "$slurm_dir"/slurm_files/scheduling/*.slurm; do
  sbatch "$slurm_file"
done
""")

    def generate_master_slurm(self):
        slurm_file = self.base_dir / "master.slurm"
        with open(slurm_file, "w") as f:
            f.write(f"""#!/bin/bash
#SBATCH --job-name=master_job
#SBATCH --output=output/master_job_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=12:00:00  
#SBATCH --mem=2G 

slurm_dir=$1

# Soumettre taskset.slurm
taskset_job_id=$(sbatch "$slurm_dir"/slurm_files/taskset/all_tasksets.slurm "$slurm_dir" | awk '{{print $4}}')
echo "Taskset job submitted with ID $taskset_job_id"

# Soumettre assignment.slurm avec dépendance sur taskset.slurm
assignment_job_id=$(sbatch --dependency=afterok:$taskset_job_id "$slurm_dir"/slurm_files/assignment/all_assignments.slurm "$slurm_dir" | awk '{{print $4}}')
echo "Assignment job submitted with ID $assignment_job_id"

# Soumettre scheduling.slurm avec dépendance sur assignment.slurm
scheduling_job_id=$(sbatch --dependency=afterok:$assignment_job_id "$slurm_dir"/slurm_files/scheduling/all_schedulings.slurm "$slurm_dir" | awk '{{print $4}}')
echo "Scheduling job submitted with ID $scheduling_job_id"
""")
