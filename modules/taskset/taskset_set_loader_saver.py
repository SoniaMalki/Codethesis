import os
import pickle
from pathlib import Path

class TasksetSetLoaderSaver:
    def __init__(self, main_path):
        self.taskset_path = main_path / "results" / "tasksets"
    def load(self, taskset_id):
        taskset_filename = f"{taskset_id}.pkl"
        with open(self.taskset_path / taskset_filename, 'rb') as f:
            taskset_set = pickle.load(f)
        return taskset_set


    def save(self, taskset_set_obj):
        # Save TasksetSet
        if taskset_set_obj is not None:
            os.makedirs(self.taskset_path, exist_ok=True)  # Create the tasksets directory
            taskset_filename = f"{taskset_set_obj.taskset_id}.pkl"
            with open(self.taskset_path / taskset_filename, 'wb') as f:
                pickle.dump(taskset_set_obj, f)