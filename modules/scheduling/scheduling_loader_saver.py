class SchedulingLoaderSaver:
    def __init__(self, main_path):
        self.scheduling_path = main_path / "results" / "schedulings"

    def load(self, scheduling_id):
        scheduling_filename = f"{scheduling_id}.pkl"
        with open(self.scheduling_path / scheduling_filename, 'rb') as f:
            scheduling_obj = pickle.load(f)
        return scheduling_obj

    def save(self, scheduling_obj, scheduling_id):
        # Save Scheduling
        if scheduling_obj is not None:
            os.makedirs(self.scheduling_path, exist_ok=True)  # Create the schedulings directory
            scheduling_filename = f"{scheduling_id}.pkl"
            with open(self.scheduling_path / scheduling_filename, 'wb') as f:
                pickle.dump(scheduling_obj, f)