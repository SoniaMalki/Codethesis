from pathlib import Path
import sys
import json
import threading

from modules.config.config_generator import ConfigGenerator
from modules.core.experience_loader import ExperienceLoader
from modules.analysis.result_analyzer import ResultAnalyzer
from modules.slurm.slurm_generator import SlurmGenerator


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
        experience_key (str): La clé (nom du dossier) de l'expérience.
        action (str): L'action à effectuer.
        config_type (str, optional): Le type de configuration pour run_batch_experiences.
    """
    main_path = Path(__file__).parent
    generation_path = Path(__file__).parent / "generation" / experience_key
    generation_path.mkdir(parents=True, exist_ok=True)

    # Charger experience.json depuis la racine
    experience_json_path = Path(__file__).parent / "experience.json"

    with open(experience_json_path, 'r') as f:
        experience_data = json.load(f)

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
        slurm_generator = SlurmGenerator(
            main_dir=main_path,
            generation_dir=generation_path,
            experience_key=experience_key,
            experience_data=experience_data[experience_key],
        )
        slurm_generator.generate_all_slurm()

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
