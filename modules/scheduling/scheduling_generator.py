from modules.scheduling.homogeneous_scheduler import HomogeneousScheduler
from modules.scheduling.mixed_scheduler import MixedScheduler
from time import sleep

class SchedulingGenerator:
    def __init__(self, assignment, taskset_id, assignment_id, scheduling_id, scheduling_algorithms, current_time=0):
        self.assignment = assignment
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_id = scheduling_id
        self.scheduling_algorithms = scheduling_algorithms[0].lower()  # Store in lowercase for case-insensitive comparison
        self.current_time = current_time

    def generate_scheduling(self):
        """Generates schedulings for each assignment within the TasksetSet."""

        schedulings = []  # Store schedulings for each assignment

        # Determine the scheduling algorithm once
        if self.scheduling_algorithms == "edf":
            scheduling_function = self._edf_scheduling
        elif self.scheduling_algorithms == "dm":
            scheduling_function = self._dm_scheduling
        elif self.scheduling_algorithms == "mixed":
            scheduling_function = self._mixed_scheduling
        else:
            print(f"Invalid scheduling algorithm: {self.scheduling_algorithms}. Returning None.")
            return None

        # Apply the selected scheduling function to all taskset assignments
        for taskset_assignment in self.assignment:
            self.number_of_cores = len(taskset_assignment[0])

            schedule, successfully_scheduled = scheduling_function(taskset_assignment)
            schedulings.append((schedule, successfully_scheduled))

        return schedulings  # Return a list of schedulings, one for each taskset assignment

    def _edf_scheduling(self, taskset_assignment):
        """Performs EDF scheduling."""
        scheduler = HomogeneousScheduler(
            taskset_assignment, "edf", self.number_of_cores, self.current_time
        )
        schedule, successfully_scheduled = scheduler.schedule()
        return schedule, successfully_scheduled

    def _dm_scheduling(self, taskset_assignment):
        """Performs DM scheduling."""
        scheduler = HomogeneousScheduler(
            taskset_assignment, "dm", self.number_of_cores, self.current_time
        )
        schedule, successfully_scheduled = scheduler.schedule()
        return schedule, successfully_scheduled

    def _mixed_scheduling(self, taskset_assignment):
        """Performs mixed scheduling."""
        scheduler = MixedScheduler(
            taskset_assignment, "mixed", len(taskset_assignment[0]), self.current_time
        )
        schedule, successfully_scheduled = scheduler.schedule()
        return schedule, successfully_scheduled