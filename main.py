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


def run_experience(experience_parameter_key, experience_loader):
    experience = experience_loader.load(experience_parameter_key)
    if experience:
        experience.process()


def run_batch_experiences(experience_loader, config_type):
    config_ids = experience_loader.get_config_ids(config_type)

    if not config_ids:
        print(f"Aucun ID de configuration trouvé pour le type: {config_type}")
        return

    threads = []
    for config_id in config_ids:
        thread = threading.Thread(
            target=run_experience, args=(config_id, experience_loader))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def main(experience_id=None, action=None, config_type=None):
    """
    Fonction principale pour exécuter une expérience ou analyser les résultats.

    Args:
        experience_id (str, optional): ID de l'expérience. Si None, l'utilisateur devra choisir parmi les disponibles.
        action (str): L'action à effectuer.
        config_type (str, optional): Le type de configuration pour run_batch_experiences.
    """
    main_path = Path(__file__).parent
    generation_path = Path(__file__).parent / "generation"
    db_path = generation_path / "experience.db"

    # Charger experience.json depuis la racine (pour les actions qui utilisent JSON)
    experience_json_path = Path(__file__).parent / "experience.json"
    with open(experience_json_path, 'r') as f:
        experience_data = json.load(f)

    # 1. Actions utilisant le fichier JSON (anciennes actions)
    if action == "run_experience":
        if config_type is None:
            print("Veuillez fournir un type de configuration (ex: taskset_generate_1_c4)")
            return
        run_experience(config_type, experience_loader=ExperienceLoader(
            generation_path / experience_id))

    elif action == "run_batch_experiences":
        if not config_type:
            print(
                "Veuillez fournir un type de configuration (taskset, assignment, scheduling)")
            return
        run_batch_experiences(experience_loader=ExperienceLoader(
            generation_path / experience_id), config_type=config_type)

    elif action == "analyze_results":
        if not experience_id:
            print("Veuillez fournir une ID d'expérience.")
            return
        analyzer = ResultAnalyzer(generation_path / experience_id)
        analyzer.run_analysis()

    elif action == "generate_configs":
        if experience_id not in experience_data:
            print(
                f"L'ID d'experience: {experience_id} n'existe pas. Veuillez la créer")
            return
        generator = ConfigGenerator(
            generation_path / experience_id, experience_data=experience_data[experience_id])
        generator.generate_all_configs()

    elif action == "generate_slurm_files":
        if experience_id not in experience_data:
            print(
                f"L'ID d'experience: {experience_id} n'existe pas. Veuillez la créer")
            return

        # Génération de la prime matrix
        prime_matrix_path = generation_path / \
            experience_id / "results" / "prime_matrices"
        prime_matrix_path.mkdir(parents=True, exist_ok=True)

        prime_matrix_combinations = experience_data[experience_id]["config_parameters"][
            "taskset_parameters"]["prime_exponent_hyperperiod_combinations"]
        for combination in prime_matrix_combinations:
            max_hyperperiod, max_prime, gen_limit_exponent = combination
            prime_matrix_generator = PrimeMatrixGenerator(
                main_path=generation_path / experience_id, max_hyperperiod=max_hyperperiod, max_prime=max_prime, gen_limit_exponent=gen_limit_exponent)
            prime_matrix_generator.generate_matrix()

        # Génération des fichiers SLURM
        slurm_generator = SlurmGenerator(
            main_dir=main_path,
            generation_dir=generation_path / experience_id,
            experience_key=experience_id,
            experience_data=experience_data[experience_id],
        )
        slurm_generator.generate_all_slurm()

    elif action == "generate_estimation":
        if experience_id not in experience_data:
            print(
                f"L'ID d'experience: {experience_id} n'existe pas. Veuillez la créer")
            return
        slurm_generator = SlurmGenerator(
            main_dir=main_path,
            generation_dir=generation_path / experience_id,
            experience_key=experience_id,
            experience_data=experience_data[experience_id],
        )
        slurm_generator.generate_estimation()

    # 2. Actions utilisant la base de données (nouvelles actions)
    elif action == "run_experience_db":
        if config_type is None:
            print("Veuillez fournir un ID de configuration (ex: taskset_1)")
            return

        experience_loader_db = ExperienceLoaderDB(db_path, experience_id)
        run_experience(config_type, experience_loader_db)

    elif action == "run_batch_experiences_db":
        if not config_type:
            print(
                "Veuillez fournir un type de configuration (taskset, assignment, scheduling)")
            return
        experience_loader_db = ExperienceLoaderDB(db_path, experience_id)
        run_batch_experiences(experience_loader_db, config_type)

    elif action == "generate_configs_db":
        generator = ConfigGeneratorDB(
            db_path=db_path, experience_data=experience_data[experience_id])
        generator.generate_configs_from_json(experience_data, experience_id)
        generator.close_connection()

    else:
        print(f"Action invalide: {action}")

    # 3. Sélection de l'expérience (si experience_id n'est pas fourni en argument)
    if experience_id is None:
        experience_loader_db = ExperienceLoaderDB(db_path)
        available_experiences = experience_loader_db.get_experience_ids()
        if not available_experiences:
            print("Aucune expérience disponible dans la base de données.")
            return

        print("Expériences disponibles :")
        for i, exp_id in enumerate(available_experiences):
            print(f"{i+1}. {exp_id}")

        while True:
            try:
                choice = int(
                    input("Choisissez une expérience (entrez le numéro) : "))
                if 1 <= choice <= len(available_experiences):
                    experience_id = available_experiences[choice - 1]
                    break
                else:
                    print("Choix invalide. Veuillez entrer un numéro valide.")
            except ValueError:
                print("Entrée invalide. Veuillez entrer un numéro.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Utilisation : python main.py <ID_expérience> <action> [config_type]")
        sys.exit(1)

    experience_id = sys.argv[1]
    action = sys.argv[2]
    config_type = sys.argv[3] if len(sys.argv) > 3 else None

    main(experience_id, action, config_type)
