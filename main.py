from pathlib import Path
import sys
import json
import threading

from modules.config.config_generator import ConfigGenerator
from modules.config.config_generator_db import ConfigGeneratorDB
from modules.core.experience_loader import ExperienceLoader
from modules.core.experience_loader_db import ExperienceLoaderDB
from modules.analysis.result_analyzer import ResultAnalyzer
from modules.slurm.slurm_generator import SlurmGenerator
from modules.taskset.task_parameters_generator.prime_matrix_generator import PrimeMatrixGenerator


def run_experience(experience_parameter_key, experience_path):
    experience_loader = ExperienceLoader(experience_path)
    experience = experience_loader.load(experience_parameter_key)
    if experience:
        experience.process()


def run_batch_experiences(config_type, generation_path):
    experience_loader = ExperienceLoader(generation_path)
    config_file_path = experience_loader.config_files.get(config_type)

    if not config_file_path:
        print(f"Invalid config type: {config_type}")
        return

    with open(generation_path / config_file_path, 'r') as f:
        configurations = json.load(f)

    threads = []
    for config_key in configurations.keys():
        thread = threading.Thread(
            target=run_experience, args=(config_key, generation_path))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def get_default_key(config_type, generation_path):
    experience_loader = ExperienceLoader(generation_path)
    config_file_path = experience_loader.config_files.get(config_type)

    if not config_file_path:
        config_file_path = "config_files/tasksets.json"

    with open(generation_path / config_file_path, 'r') as f:
        configurations = json.load(f)

    return next(iter(configurations))


def main(experience_key, action, config_type=None):
    """
    Fonction principale pour exécuter une expérience ou analyser les résultats.

    Args:
        experience_id (str, optional): ID de l'expérience. Si None, l'utilisateur devra choisir parmi les disponibles.
        action (str): L'action à effectuer.
        config_type (str, optional): Le type de configuration pour run_batch_experiences.
    """
    main_path = Path(__file__).parent
    generation_path = Path(__file__).parent / "generation" / experience_key
    db_path = Path(__file__).parent / "generation" / "experience.db"

    # Charger experience.json depuis la racine
    experience_json_path = Path(__file__).parent / "experience.json"

    with open(experience_json_path, 'r') as f:
        experience_data = json.load(f)

    if experience_key not in experience_data:
        print(
            f"La clé d'experience: {experience_key} n'existe pas. Veuillez la créer")
        return

    generation_path.mkdir(parents=True, exist_ok=True)

    if action == "run_experience":
        if config_type is None:
            print("Veuillez fournir un type de configuration (ex: taskset_generate_1_c4)")
            return

        run_experience(config_type, generation_path)

    elif action == "run_batch_experiences":
        if not config_type:
            print(
                "Veuillez fournir un type de configuration (taskset, assignment, scheduling)"
            )
            return
        run_batch_experiences(config_type, generation_path)

    elif action == "analyze_results":
        analyzer = ResultAnalyzer(generation_path)
        analyzer.run_analysis()

    elif action == "generate_configs":
        generator = ConfigGenerator(
            generation_path, experience_data=experience_data[experience_key])
        generator.generate_all_configs()

    elif action == "generate_slurm_files":
        # Génération de la prime matrix
        prime_matrix_path = generation_path / "results" / "prime_matrices"
        prime_matrix_path.mkdir(parents=True, exist_ok=True)

        prime_matrix_combinations = experience_data[experience_key]["config_parameters"][
            "taskset_parameters"]["prime_exponent_hyperperiod_combinations"]
        for combination in prime_matrix_combinations:
            max_hyperperiod, max_prime, gen_limit_exponent = combination
            prime_matrix_generator = PrimeMatrixGenerator(
                main_path=generation_path, max_hyperperiod=max_hyperperiod, max_prime=max_prime, gen_limit_exponent=gen_limit_exponent)
            prime_matrix_generator.generate_matrix()

        # Génération des fichiers SLURM
        slurm_generator = SlurmGenerator(
            main_dir=main_path,
            generation_dir=generation_path,
            experience_key=experience_key,
            experience_data=experience_data[experience_key],
        )
        slurm_generator.generate_all_slurm()
    elif action == "generate_estimation":
        slurm_generator = SlurmGenerator(
            main_dir=main_path,
            generation_dir=generation_path,
            experience_key=experience_key,
            experience_data=experience_data[experience_key],
        )
        slurm_generator.generate_estimation()

    # Actions utilisant la base de données
    elif action == "run_experience_db":
        if config_type is None:
            print("Veuillez fournir un ID de configuration (ex: taskset_1)")
            return

        experience_loader_db = ExperienceLoaderDB(db_path, experience_key)
        run_experience(config_type, experience_loader_db)

    elif action == "run_batch_experiences_db":
        if not config_type:
            print(
                "Veuillez fournir un type de configuration (taskset, assignment, scheduling)"
            )
            return
        experience_loader_db = ExperienceLoaderDB(db_path, experience_key)
        run_batch_experiences(experience_loader_db, config_type)

    elif action == "generate_configs_db":
        generator = ConfigGeneratorDB(db_path=db_path)
        generator.generate_configs_from_json(experience_data, experience_key)
        generator.close_connection()
    else:
        print(f"Action invalide: {action}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Utilisation : python main.py <clé_expérience> <action> [config_type]"
        )
        sys.exit(1)

    experience_key = sys.argv[1]
    action = sys.argv[2]
    config_type = sys.argv[3] if len(sys.argv) > 3 else None

    main(experience_key, action, config_type)
