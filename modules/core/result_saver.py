import os
import pickle
from pathlib import Path

class ResultSaver:
    def __init__(self, main_path):
        self.results_path = main_path / "results"  # Path to the results directory
        os.makedirs(self.results_path, exist_ok=True)  # Create the directory if it doesn't exist

    def save(self, experience):
        """
        Saves the results of the experience to files.

        Args:
            experience (Experience): The Experience object containing the results.
        """
        # Save TasksetSet
        if experience.taskset_set_obj is not None:
            taskset_path = self.results_path / "tasksets"
            os.makedirs(taskset_path, exist_ok=True)  # Create the tasksets directory
            taskset_filename = f"taskset_{experience.taskset_set.taskset_set_number}.pkl"
            with open(taskset_path / taskset_filename, 'wb') as f:
                pickle.dump(experience.taskset_set, f)

        # Save Assignment
        if experience.assignment_obj is not None:
            assignment_path = self.results_path / "assignments"
            os.makedirs(assignment_path, exist_ok=True)  # Create the assignments directory
            assignment_filename = f"assignment_{experience.assignment_obj.assignment_id}.pkl"
            with open(assignment_path / assignment_filename, 'wb') as f:
                pickle.dump(experience.assignment_obj, f)

        # Save Scheduling
        if experience.scheduling_obj is not None:
            scheduling_path = self.results_path / "schedules"
            os.makedirs(scheduling_path, exist_ok=True)  # Create the schedules directory
            scheduling_filename = f"scheduling_{experience.scheduling_obj.scheduling_id}.pkl"
            with open(scheduling_path / scheduling_filename, 'wb') as f:
                pickle.dump(experience.scheduling_obj, f)