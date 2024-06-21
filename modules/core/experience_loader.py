import json
import os
from pathlib import Path
from modules.core.experience import Experience


class ExperienceLoader:
    def __init__(self, main_path):
        self.main_path = main_path


    def load(self, filename, experience_parameter_index="1"):
        """
        Loads an Experience object from a JSON file.

        Args:
            filename (str): The path to the JSON file.
            experience_parameter_index (str, optional): The index of the experience to load. Defaults to first key.

        Returns:
            Experience: An Experience object containing the loaded data.
        """
        with open(f"{self.main_path}/{filename}", 'r') as f:
            experience_data = json.load(f)

        # Validate the experience_parameter_index
        if experience_parameter_index in experience_data:
            experience_parameters = experience_data[experience_parameter_index]
        else:
            experience_parameter_index = list(experience_data.keys())[0]
            print(f"Invalid experience parameter index: {experience_parameter_index}. Defaulting to index to first key: {experience_parameter_index}.")

        # Get the experience parameters based on the index
        taskset_parameters = experience_data[experience_parameter_index]["taskset"]
        assignment_parameters = experience_data[experience_parameter_index]["assignment"]
        scheduling_parameters = experience_data[experience_parameter_index]["scheduling"]

        # Create the Experience object
        return Experience(
            taskset_parameters=taskset_parameters,
            assignment_parameters=assignment_parameters,
            scheduling_parameters=scheduling_parameters,
            main_path=self.main_path
        )