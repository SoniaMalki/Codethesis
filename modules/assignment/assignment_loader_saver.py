import os
import pickle

from modules.utils.db_utils import DBUtils


class AssignmentLoaderSaver:
    def __init__(self, main_path, db_path):
        self.assignment_path = main_path / "results" / "assignments"
        self.db_utils = DBUtils(db_path)

    def load(self, assignment_id):
        assignment_filename = f"{assignment_id}.pkl"
        with open(self.assignment_path / assignment_filename, 'rb') as f:
            assignment_obj = pickle.load(f)
        return assignment_obj

    def save(self, assignment_obj, assignment_id):
        # Save Assignment
        if assignment_obj is not None:
            # Create the assignments directory
            os.makedirs(self.assignment_path, exist_ok=True)
            assignment_filename = f"{assignment_id}.pkl"
            with open(self.assignment_path / assignment_filename, 'wb') as f:
                pickle.dump(assignment_obj, f)

            self.db_utils.update_result_file_path(config_id=assignment_id, config_type="assignment",
                                                  file_path=assignment_filename)
