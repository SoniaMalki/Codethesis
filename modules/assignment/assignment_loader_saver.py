import os
import pickle

class AssignmentLoaderSaver:
    def __init__(self, main_path):
        self.assignment_path = main_path / "results" / "assignments"

    def load(self, assignment_id):
        assignment_filename = f"{assignment_id}.pkl"
        with open(self.assignment_path / assignment_filename, 'rb') as f:
            assignment_obj = pickle.load(f)
        return assignment_obj

    def save(self, assignment_obj, assignment_id):
        # Save Assignment
        if assignment_obj is not None:
            os.makedirs(self.assignment_path, exist_ok=True)  # Create the assignments directory
            assignment_filename = f"{assignment_id}.pkl"
            with open(self.assignment_path / assignment_filename, 'wb') as f:
                pickle.dump(assignment_obj, f)