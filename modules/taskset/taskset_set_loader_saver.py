import os
import pickle
from pathlib import Path

from modules.utils.db_utils import DBUtils


class TasksetSetLoaderSaver:
    def __init__(self, main_path, db_path, result_path):
        self.taskset_path = result_path / "tasksets"
        self.db_utils = DBUtils(db_path)

    def load(self, taskset_id):
        taskset_filename = f"{taskset_id}.pkl"
        with open(self.taskset_path / taskset_filename, 'rb') as f:
            taskset_set = pickle.load(f)
        return taskset_set

    def save(self, taskset_set_obj):
        # Save TasksetSet
        if taskset_set_obj is not None:
            # Create the tasksets directory
            os.makedirs(self.taskset_path, exist_ok=True)
            taskset_filename = f"{taskset_set_obj.taskset_id}.pkl"
            with open(self.taskset_path / taskset_filename, 'wb') as f:
                pickle.dump(taskset_set_obj, f)
            self.db_utils.update_result_file_path(config_id=taskset_set_obj.taskset_id, config_type="taskset",
                                                  file_path=taskset_filename)
