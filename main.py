from pathlib import Path
import subprocess
import sys
import json
import threading

from modules.core.experience_loader import ExperienceLoader
from modules.analysis.result_analyzer import ResultAnalyzer


def run_experience(experience_parameter_key):
    experience_loader = ExperienceLoader(Path(__file__).parent)
    experience = experience_loader.load(experience_parameter_key)
    if experience:
        experience.process()


def run_batch_experiences(config_type):
    experience_loader = ExperienceLoader(Path(__file__).parent)
    config_file_path = experience_loader.config_files.get(config_type)

    if not config_file_path:
        print(f"Invalid config type: {config_type}")
        return

    with open(Path(__file__).parent / config_file_path, 'r') as f:
        configurations = json.load(f)

    threads = []
    for config_key in configurations.keys():
        thread = threading.Thread(target=run_experience, args=(config_key,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def get_default_key(config_type):
    experience_loader = ExperienceLoader(Path(__file__).parent)
    config_file_path = experience_loader.config_files.get(config_type)

    if not config_file_path:
        config_file_path = "config_files/tasksets.json"

    with open(Path(__file__).parent / config_file_path, 'r') as f:
        configurations = json.load(f)

    return next(iter(configurations))


def main(action="run_experience", experience_parameter_key=None):
    """
    Fonction principale pour exécuter une expérience ou analyser les résultats.

    Args:
        action (str, optional): L'action à effectuer. Peut être "run_experience", "analyze_results", "generate_configs" ou "run_batch_experiences". Défaut "run_experience".
        experience_parameter_key (str, optional): La clé de l'expérience à charger ou le type de configuration. Défaut None.
    """

    if action == "run_experience":
        if not experience_parameter_key:
            experience_parameter_key = get_default_key("taskset")
        run_experience(experience_parameter_key)

    elif action == "run_batch_experiences":
        if not experience_parameter_key:
            print("Please provide a config type (taskset, assignment, scheduling)")
            return
        run_batch_experiences(experience_parameter_key)

    elif action == "analyze_results":
        analyzer = ResultAnalyzer(Path(__file__).parent)
        analyzer.run_analysis()

    elif action == "generate_configs":
        subprocess.run(["python3", "./generate_experiences_json.py"])

    else:
        print(f"Action invalide: {action}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        action = sys.argv[1]
        experience_parameter_key = sys.argv[2]
        main(action, experience_parameter_key)
    elif len(sys.argv) == 2:
        action = sys.argv[1]
        main(action)
    else:
        main()
