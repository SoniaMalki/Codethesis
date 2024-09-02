import os
import sys
import json
from pathlib import Path

from modules.config.config_generator import ConfigGenerator
from modules.core.experience_loader import ExperienceLoader
from modules.analysis.result_analyzer import ResultAnalyzer
from modules.slurm.slurm_generator import SlurmGenerator
from modules.taskset.task_parameters_generator.prime_matrix_generator import PrimeMatrixGenerator
from modules.utils.database_concatenator import DatabaseConcatenator
from modules.utils.database_merger import DatabaseMerger
from modules.utils.db_utils import DBUtils

global_scratch = os.getenv('GLOBALSCRATCH')

if global_scratch is None:
    print("La variable d'environnement GLOBALSCRATCH n'est pas définie.")
    global_scratch = os.getenv('HOME')
    print('Utilisation HOME à la place de GLOBALSCRATCH')
    if global_scratch is None:
        raise FileNotFoundError

global_scratch = Path(global_scratch)
print(f"Le chemin de global_scratch est: {global_scratch}")


def run_experience(experience_parameter_key, experience_loader):
    print(f"Running experience with parameter key: {experience_parameter_key}")
    experience = experience_loader.load(experience_parameter_key)
    if experience:
        print(f"Processing experience: {experience_parameter_key}")
        experience.process()


def run_batch_experiences(experience_loader, config_type):
    print(f"Running batch experiences for config type: {config_type}")
    config_ids = experience_loader.get_config_ids(config_type)

    if not config_ids:
        print(f"Aucun ID de configuration trouvé pour le type: {config_type}")
        return

    for config_id in config_ids:
        print(f"Running experience for config ID: {config_id}")
        run_experience(config_id, experience_loader)


def main(action, index, experience_id, experience_action=None):
    """
    Fonction principale pour exécuter une expérience ou analyser les résultats.

    Args:
        action (str): L'action à effectuer.
        index (str): index de experience.json
        experience_id (str, optional): ID de l'expérience. Si None, l'utilisateur devra choisir parmi les disponibles.
        experience_action (str, optional): Le type d'action pour run_batch_experiences.
    """
    print(
        f"Main function started with action: {action}, experience_id: {experience_id}, experience_action: {experience_action}")
    main_path = Path(__file__).parent
    generation_path = global_scratch / "generation"
    db_path = generation_path / f"experience_{index}.db"
    experience_json_path = Path(__file__).parent / f"experience_{index}.json"
    result_path = generation_path / f"results_{index}"
    plots_path = generation_path / f"plots_{index}"

    # Charger experience.json
    print("Loading experience.json")
    with open(experience_json_path, 'r') as f:
        experience_data = json.load(f)

    if not experience_id:
        print("Veuillez fournir une ID d'expérience.")
        return

    if experience_id not in experience_data:
        print(
            f"L'ID d'experience: {experience_id} n'existe pas. Veuillez la créer")
        return

    if action == "analyze_results":
        print(f"Analyzing results for experience ID: {experience_id}")
        result_path.mkdir(parents=True, exist_ok=True)
        plots_path.mkdir(parents=True, exist_ok=True)
        analyzer = ResultAnalyzer(
            db_path, experience_id, plots_path, result_path)
        analyzer.run_analysis()

    elif action == "generate_slurm_files":
        # Génération de la prime matrix
        print(f"Generating prime matrix for experience ID: {experience_id}")
        result_path.mkdir(parents=True, exist_ok=True)

        prime_matrix_combinations = experience_data[experience_id]["config_parameters"][
            "taskset_parameters"]["prime_exponent_hyperperiod_combinations"]
        for combination in prime_matrix_combinations:
            max_hyperperiod, max_prime, gen_limit_exponent = combination
            prime_matrix_generator = PrimeMatrixGenerator(
                main_path=generation_path, result_path=result_path, max_hyperperiod=max_hyperperiod, max_prime=max_prime, gen_limit_exponent=gen_limit_exponent)
            prime_matrix_generator.generate_matrix()

        # Génération des fichiers SLURM
        print(f"Generating SLURM files for experience ID: {experience_id}")
        slurm_generator = SlurmGenerator(
            main_path=main_path,
            generation_path=generation_path,
            db_path=db_path,
            index=index,
            experience_id=experience_id,
            experience_data=experience_data[experience_id],
        )
        slurm_generator.generate_all_slurm()

    elif action == "run_experience":
        print(f"Running experience with action: {experience_action}")
        result_path.mkdir(parents=True, exist_ok=True)
        experience_loader_db = ExperienceLoader(
            db_path, result_path, experience_id)
        run_experience(experience_action, experience_loader_db)

    elif action == "run_batch_experiences":
        print(f"Running batch experiences with action: {experience_action}")
        result_path.mkdir(parents=True, exist_ok=True)
        experience_loader_db = ExperienceLoader(
            db_path, result_path, experience_id)
        run_batch_experiences(experience_loader_db, experience_action)

    elif action == "generate_configs":
        print(f"Generating configs for experience ID: {experience_id}")
        generator = ConfigGenerator(
            db_path=db_path, experience_data=experience_data[experience_id])
        generator.generate_configs_from_json(experience_data, experience_id)

    elif action == "generate_slurm_scripts":
        print(f"Generating SLURM scripts for experience ID: {experience_id}")
        slurm_generator = SlurmGenerator(
            main_path=main_path,
            generation_path=generation_path,
            db_path=db_path,
            index=index,
            experience_id=experience_id,
            experience_data=experience_data[experience_id],
        )
        slurm_generator.generate_full_pipeline_slurm(include_analyze=False)
        print(f"SLURM scripts generated for experience ID: {experience_id}")

    elif action == "merge_databases":
        print(
            f"Merging databases v1 and v2 into merged.db for experience ID: {experience_id}")
        db_path_v1 = generation_path / "v1.db"
        db_path_v2 = generation_path / "v2.db"
        merged_db_path = generation_path / "merged.db"
        merger = DatabaseMerger(db_path_v1, db_path_v2, merged_db_path)
        merger.merge_tables()
        print(
            f"Databases merged successfully for experience ID: {experience_id}")

    elif action == "concatenate_databases":
        db_paths = {
            '2': generation_path / 'db_2.db',
            '3': generation_path / 'db_3.db'
        }

        structure_db_path = generation_path / 'big.db'
        result_folder = generation_path / "results"

        integrator = DatabaseConcatenator(
            db_paths, structure_db_path, result_folder)
        integrator.integrate_databases()

    else:
        print(f"Action invalide: {action}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Utilisation : python main.py <action> <index> <experience_id> [experience_action]")
        sys.exit(1)

    action = sys.argv[1]
    index = sys.argv[2]
    experience_id = sys.argv[3]
    experience_action = sys.argv[4] if len(sys.argv) > 4 else None

    print(
        f"Script started with action: {action}, index: {index}, experience_id: {experience_id}, experience_action: {experience_action}")
    main(action, index, experience_id, experience_action)
    print("Script execution completed")
