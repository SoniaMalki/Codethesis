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
        if experience_parameter_index in experience_data:
            experience_parameters = experience_data[experience_parameter_index]
        else:
            print(f"Invalid experience parameter index: {experience_parameter_index}. Defaulting to index 1.")
            experience_parameter_index = "1"  # Default to index 1 if invalid

        # Get the experience data based on the index
        taskset_data = experience_data[experience_parameter_index]["taskset"]
        assignment_data = experience_data[experience_parameter_index]["assignment"]
        scheduling_data = experience_data[experience_parameter_index]["scheduling"]

        # Create the Experience object
        return Experience(
            taskset_parameters=taskset_data,
            assignment_parameters=assignment_data,
            scheduling_parameters=scheduling_data,
            main_path=self.current_path
        )