from modules.scheduling.scheduling import Scheduling
from modules.scheduling.scheduling_algorithms.earliest_deadline_first import EarliestDeadlineFirst
from modules.scheduling.scheduling_set import SchedulingSet
from modules.scheduling.homogeneous_scheduler import HomogeneousScheduler
from modules.scheduling.mixed_scheduler import MixedScheduler

import time

class SchedulingGenerator:
    def __init__(self, taskset_set_obj, assignment_set_obj, taskset_id, assignment_id, scheduling_id, scheduling_algorithms):
        self.taskset_set = taskset_set_obj
        self.assignment_set = assignment_set_obj
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_id = scheduling_id
        self.scheduling_algorithms = scheduling_algorithms[0].lower()  # Store in lowercase for case-insensitive comparison        
        self.number_of_cores = self.assignment_set.number_of_cores


    def generate_scheduling_set(self):
        """Generates schedulings for each assignment within the TasksetSet."""

        scheduling_list = []  # Store schedulings for each assignment

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

        for taskset, assignment in zip(self.taskset_set, self.assignment_set):
            if assignment.success: 
                schedule, success = scheduling_function(taskset=taskset, assignment=assignment)
                scheduling_list.append(Scheduling(success=success, schedule=schedule))
                print(scheduling_list[0].__str__(end_time=19))
                print(f'success: {success}')

            else:
                scheduling_list.append(Scheduling(schedule=[], success=0))

        scheduling = SchedulingSet(scheduling_id=self.scheduling_id, taskset_id=self.taskset_id, assignment_id=self.assignment_id, scheduling_algorithms=self.scheduling_algorithms, scheduling_list=scheduling_list)  # Store assignments for each taskset
        return scheduling  # Return a list of assignments, one for each taskset



    def _edf_scheduling(self, taskset, assignment):
        """Performs EDF scheduling."""
        scheduler = EarliestDeadlineFirst(
            taskset=taskset,
            assignment=assignment, 
            number_of_cores=self.number_of_cores
        )
        schedule, successfully_scheduled = scheduler.schedule()

        return schedule, successfully_scheduled

    def _dm_scheduling(self, taskset, assignment):
        """Performs DM scheduling."""
        scheduler = HomogeneousScheduler(
            taskset,
            assignment
        )
        schedule, successfully_scheduled, _ = scheduler.schedule()
        return schedule, successfully_scheduled

    def _mixed_scheduling(self, taskset, assignment):
        """Performs mixed scheduling."""
        scheduler = MixedScheduler(
            taskset,
            assignment
        )
        schedule, successfully_scheduled = scheduler.schedule()
        return schedule, successfully_scheduled
    


