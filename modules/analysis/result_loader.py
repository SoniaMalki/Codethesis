import os
import pickle
import json

from modules.scheduling.composite_scheduling import CompositeScheduling
from modules.scheduling.scheduling import Scheduling


class ResultLoader:
    def __init__(self, current_path):
        self.current_path = current_path

        self.result_directory = current_path / "results"
        self.taskset_configs_json_path = current_path / "config_files/tasksets.json"
        self.assignment_configs_json_path = current_path / "config_files/assignments.json"
        self.scheduling_configs_json_path = current_path / "config_files/schedulings.json"

        with open(self.taskset_configs_json_path, "r") as f:
            self.taskset_configs = json.load(f)
        with open(self.assignment_configs_json_path, "r") as f:
            self.assignment_configs = json.load(f)
        with open(self.scheduling_configs_json_path, "r") as f:
            self.scheduling_configs = json.load(f)

    def load_data(self, file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)

    def get_experiment_info(self, experience_id):
        if experience_id in self.taskset_configs:
            return self.taskset_configs[experience_id], "taskset"
        elif experience_id in self.assignment_configs:
            return self.assignment_configs[experience_id], "assignment"
        elif experience_id in self.scheduling_configs:
            return self.scheduling_configs[experience_id], "scheduling"
        else:
            return None, None

    def load_results(self):
        assignment_sets = []
        scheduling_sets = []

        for dirpath, dirnames, filenames in os.walk(self.result_directory):
            for filename in filenames:
                if filename.endswith(".pkl"):
                    file_path = os.path.join(dirpath, filename)
                    data_obj = self.load_data(file_path)
                    config, exp_type = self.get_experiment_info(filename[:-4])

                    if exp_type == "assignment":
                        assignment_sets.append(data_obj)
                    elif exp_type == "scheduling":
                        scheduling_sets.append(data_obj)

        return assignment_sets, scheduling_sets
