from pathlib import Path
import sys
import subprocess

from modules.core.experience_loader import ExperienceLoader
from modules.analysis.result_analyzer import ResultAnalyzer


def main(action="run_experience", experience_parameter_key="taskset_generate_1_c2"):
    """
    Fonction principale pour exécuter une expérience ou analyser les résultats.

    Args:
        action (str, optional): L'action à effectuer. Peut être "run_experience", "analyze_results" ou "generate_configs". Défaut "run_experience".
        experience_parameter_key (str, optional): La clé de l'expérience à charger. Défaut "taskset_generate_1_c2".
    """

    if action == "run_experience":
        experience_loader = ExperienceLoader(Path(__file__).parent)
        experience = experience_loader.load(experience_parameter_key)
        experience.process()

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
        print(
            f"No experience parameter key given. Defaulting to key 'taskset_generate_1_c2'.")
        main()
