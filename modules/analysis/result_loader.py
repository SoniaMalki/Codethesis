import os
from pathlib import Path
import pickle
import json
import time
from unittest import result

from modules.scheduling.composite_scheduling import CompositeScheduling
from modules.scheduling.scheduling import Scheduling
from modules.utils.db_utils import DBUtils


class ResultLoader:
    def __init__(self, db_path, experience_id, result_path):
        print(f"Initializing ResultLoader for experience ID: {experience_id}")
        self.db_utils = DBUtils(db_path)
        self.experience_id = experience_id
        self.result_path = result_path
        print("ResultLoader initialized successfully")

    def load_data(self, file_path):
        # print(f"Loading data from {file_path}")
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        # print(f"Data loaded from {file_path}")
        return data

    def load_results(self):
        print("Loading results from database")
        taskset_sets = []
        assignment_sets = []
        scheduling_sets = []

        for config_type in ["taskset", "assignment", "scheduling"]:
            config_ids = self.db_utils.get_config_ids_for_experience(
                self.experience_id, config_type)
            for config_id in config_ids:
                file_path = self.result_path / \
                    (config_type + "s") / f"{config_id}.pkl"
                if file_path.exists():
                    # print(
                    #     f"Loading {config_type} data for ID: {config_id}")
                    data_obj = self.load_data(file_path)
                    if config_type == "taskset":
                        taskset_sets.append(data_obj)
                    elif config_type == "assignment":
                        assignment_sets.append(data_obj)
                    elif config_type == "scheduling":
                        scheduling_sets.append(data_obj)
                else:
                    print(
                        f"{config_type.capitalize()} file {file_path} does not exist")

        print("Results loaded successfully")
        return taskset_sets, assignment_sets, scheduling_sets
