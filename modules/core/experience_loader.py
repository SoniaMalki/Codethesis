import json
import os
from pathlib import Path
from modules.core.experience import Experience


class ExperienceLoader:
    def __init__(self, main_path):
        self.current_path = main_path


    def load(self, filename, experience_parameter_index="1"):
        """
        Loads an Experience object from a JSON file.

        Args:
            filename (str): The path to the JSON file.
            experience_parameter_index (str, optional): The index of the experience to load. Defaults to "0".

        Returns:
            Experience: An Experience object containing the loaded data.
        """
        with open(f"{self.current_path}/{filename}", 'r') as f:
            experience_data = json.load(f)

        # Validate the experience_parameter_index
        if int(experience_parameter_index) >= 0 and int(experience_parameter_index) < len(experience_data):
            experience_parameters = experience_data[experience_parameter_index]
        else:
            print(f"Invalid experience parameter index: {experience_parameter_index}. Defaulting to index 1.")
            experience_parameters = experience_data["1"]  # Default to index 0 if invalid

        return Experience(**experience_parameters)