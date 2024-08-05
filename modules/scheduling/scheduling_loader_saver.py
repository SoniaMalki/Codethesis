import os
import pickle

from modules.utils.db_utils import DBUtils


class SchedulingLoaderSaver:
    def __init__(self, main_path, db_path):
        self.scheduling_path = main_path / "results" / "schedulings"
        self.expected_scheduling_path = main_path / \
            "tests" / "results_test" / "expected_schedulings"

        self.db_utils = DBUtils(db_path=db_path)

    def load(self, scheduling_id):
        scheduling_filename = f"{scheduling_id}.pkl"
        with open(self.scheduling_path / scheduling_filename, 'rb') as f:
            scheduling_obj = pickle.load(f)
        return scheduling_obj

    def save(self, scheduling_obj, scheduling_id):
        # Save Scheduling
        if scheduling_obj is not None:
            # Create the schedulings directory
            os.makedirs(self.scheduling_path, exist_ok=True)
            scheduling_filename = f"{scheduling_id}.pkl"
            with open(self.scheduling_path / scheduling_filename, 'wb') as f:
                # Supprimer scheduling_list avant la sauvegarde pour économie espace
                for schedule in scheduling_obj:
                    schedule.schedule = None
                pickle.dump(scheduling_obj, f)
            self.db_utils.update_result_file_path(config_id=scheduling_id, config_type="scheduling",
                                                  file_path=scheduling_filename)

    def load_test_expected_result(self, scheduling_id, experience, scheduling_algorithm, non_preemption_time_variant2):

        scheduling_filename = f"expected_scheduling_results_{experience}_{scheduling_algorithm}_{non_preemption_time_variant2}.pklr"
        filepath = self.expected_scheduling_path / scheduling_filename
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return pickle.load(f)
        else:
            return None

    def save_test_expected_result(self, scheduling_obj, scheduling_id, experience, scheduling_algorithm, non_preemption_time_variant2):
        if scheduling_obj is not None:
            os.makedirs(self.expected_scheduling_path, exist_ok=True)
            scheduling_filename = f"expected_scheduling_results_{experience}_{scheduling_algorithm}_{non_preemption_time_variant2}.pklr"
            with open(self.expected_scheduling_path / scheduling_filename, 'wb') as f:
                pickle.dump(scheduling_obj, f)
