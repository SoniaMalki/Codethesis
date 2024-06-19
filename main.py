import sys
import datetime
import pickle
import os
import json
from pathlib import Path
import time

from modules.core.experience_loader import ExperienceLoader
from modules.core.result_saver import ResultSaver
current_path = Path(__file__).parent


def main(experience_parameter_index="1"):
    """
    Main function to run an experiment based on the experience.json configuration.

    Args:
        experience_parameter_index (str, optional): The index of the experience to load from experience.json. Defaults to "0".
    """

    # Load the experience
    experience_loader = ExperienceLoader(Path(__file__).parent)
    experience = experience_loader.load("config_files/experiences.json", experience_parameter_index)

    # Process the experience
    experience.process()

    # Save the results
    result_saver = ResultSaver(Path(__file__).parent)
    result_saver.save(experience)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        experience_parameter_index = sys.argv[1]
        main(experience_parameter_index)
    else:
        print(f"No experience parameter index given. Defaulting to index 1.")
        main()