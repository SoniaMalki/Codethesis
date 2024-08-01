import json
import os
from pathlib import Path
from modules.core.experience import Experience


class ExperienceLoader:
    def __init__(self, main_path):
        self.main_path = main_path
        self.config_files = {
            "taskset": "config_files/tasksets.json",
            "assignment": "config_files/assignments.json",
            "scheduling": "config_files/schedulings.json",
            "experience": "config_files/experiences.json"  # Ajouter experiences.json
        }

        for file_path in self.config_files.values():
            (self.main_path / file_path).parent.mkdir(parents=True, exist_ok=True)

    def load(self, experience_parameter_key):
        """
        Loads an Experience object from the appropriate JSON configuration file based on the given key.

        Args:
            experience_parameter_key (str): The key of the experience to load.

        Returns:
            Experience: An Experience object containing the loaded data.
        """

        # Vérifier si la clé est un nombre, ce qui indique le fichier experiences.json
        if experience_parameter_key.isdigit():
            filename = self.config_files.get("experience")
        else:
            # Déterminer le type d'expérience (taskset, assignment ou scheduling)
            experience_type = experience_parameter_key.split('_')[0]
            filename = self.config_files.get(experience_type)

        if not filename:
            print(
                f"Error: Invalid experience type or key '{experience_parameter_key}'.")
            return None

        with open(f"{self.main_path}/{filename}", 'r') as f:
            experience_data = json.load(f)

        if experience_parameter_key not in experience_data:
            print(
                f"Error: Experience parameter key '{experience_parameter_key}' not found in '{filename}'.")
            return None

        # Charger les paramètres de l'expérience
        experience_params = experience_data[experience_parameter_key]

        # Gérer les cas où certains paramètres peuvent être manquants
        taskset_parameters = experience_params.get(
            "taskset", {"action": "none"})
        assignment_parameters = experience_params.get(
            "assignment", {"action": "none"})
        scheduling_parameters = experience_params.get(
            "scheduling", {"action": "none"})

        # Créer l'objet Experience
        return Experience(
            taskset_parameters=taskset_parameters,
            assignment_parameters=assignment_parameters,
            scheduling_parameters=scheduling_parameters,
            main_path=self.main_path
        )
