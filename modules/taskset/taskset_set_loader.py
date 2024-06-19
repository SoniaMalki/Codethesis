import pickle
from pathlib import Path

class TasksetSetLoader:
    def __init__(self):
        self.results_path = Path(__file__).parent.parent / "results" / "tasksets"

    def load(self, taskset_id):
        """
        Loads a TasksetSet object from a file.

        Args:
            taskset_id (str): The ID of the taskset to load.

        Returns:
            TasksetSet: The loaded TasksetSet object.
        """
        taskset_filename = f"taskset_{taskset_id}.pkl"
        with open(self.results_path / taskset_filename, 'rb') as f:
            taskset_set = pickle.load(f)
        return taskset_set