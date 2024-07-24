import sys
import datetime
import pickle
import os
import json
from pathlib import Path
import time

from modules.core.experience_loader import ExperienceLoader
current_path = Path(__file__).parent


def main(experience_parameter_key="taskset_generate_1_c2"):
    """
    Main function to run an experiment based on the configuration files.

    Args:
        experience_parameter_key (str, optional): The key of the experience to load. Defaults to "taskset_generate_1_c2".
    """

    # Load the experience
    experience_loader = ExperienceLoader(Path(__file__).parent)
    experience = experience_loader.load(experience_parameter_key)

    # Process the experience
    experience.process()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        experience_parameter_key = sys.argv[1]
        main(experience_parameter_key)
    else:
        print(
            f"No experience parameter key given. Defaulting to key 'taskset_generate_1_c2'.")
        main()
