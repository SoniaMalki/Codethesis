from modules.scheduling.scheduling import Scheduling
from modules.scheduling.scheduling_algorithms.combined_scheduler import CombinedScheduler
from modules.scheduling.scheduling_set import SchedulingSet
from modules.scheduling.scheduling_algorithms.earliest_deadline_first import EarliestDeadlineFirst
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant1 import EarliestDeadlineFirstVariant1
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant2 import EarliestDeadlineFirstVariant2
from modules.scheduling.scheduling_algorithms.deadline_monotonic import DeadlineMonotonic
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant1 import DeadlineMonotonicVariant1
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant2 import DeadlineMonotonicVariant2
from modules.utils.busy_period_generator import BusyPeriodGenerator

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
        elif self.scheduling_algorithms == "edfv1":
            scheduling_function = self._edf_v1_scheduling
        elif self.scheduling_algorithms == "edfv2":
            scheduling_function = self._edf_v2_scheduling
        elif self.scheduling_algorithms == "dm":
            scheduling_function = self._dm_scheduling
        elif self.scheduling_algorithms == "dmv1":
            scheduling_function = self._dm_v1_scheduling
        elif self.scheduling_algorithms == "dmv2":
            scheduling_function = self._dm_v2_scheduling
        elif self.scheduling_algorithms == "combined":
            scheduling_function = self._combined_scheduling
        else:
            print(f"Invalid scheduling algorithm: {self.scheduling_algorithms}. Returning None.")
            return None

        # Apply the selected scheduling function to all taskset assignments

        for taskset, assignment in zip(self.taskset_set, self.assignment_set):
            if assignment.success: 
                schedule, success, scheduler_name = scheduling_function(taskset=taskset, assignment=assignment)
                scheduling_list.append(Scheduling(success=success, schedule=schedule, scheduler_name=scheduler_name))
                if success:
                    print(scheduling_list[0].__str__(end_time=10000))
                print(f'success: {success}')

            else:
                scheduling_list.append(Scheduling(schedule=[], success=0))
        for scheduling in scheduling_list:
            a = BusyPeriodGenerator.generate_busy_periods(scheduling=scheduling)
            print(a)
        scheduling = SchedulingSet(scheduling_id=self.scheduling_id, taskset_id=self.taskset_id, assignment_id=self.assignment_id, scheduling_algorithms=self.scheduling_algorithms, scheduling_list=scheduling_list)  # Store assignments for each taskset
        return scheduling  # Return a list of assignments, one for each taskset



    def _edf_scheduling(self, taskset, assignment):
        """Performs EDF scheduling."""
        scheduler = EarliestDeadlineFirst(
            taskset=taskset,
            assignment=assignment, 
            number_of_cores=self.number_of_cores,
            start_time=0,
            finish_time=20
        )
        schedule, successfully_scheduled = scheduler.schedule()
        print("----------")
        print(schedule)
        scheduler_name = self.scheduling_algorithms
        return schedule, successfully_scheduled, scheduler_name
    
    def _edf_v1_scheduling(self, taskset, assignment):
        """Performs EDF V1 scheduling."""
        scheduler = EarliestDeadlineFirstVariant1(
            taskset=taskset,
            assignment=assignment, 
            number_of_cores=self.number_of_cores,
            start_time=6,
            finish_time=None
        )
        schedule, successfully_scheduled = scheduler.schedule()
        scheduler_name = self.scheduling_algorithms
        return schedule, successfully_scheduled, scheduler_name
    
    def _edf_v2_scheduling(self, taskset, assignment):
        """Performs EDF V2 scheduling."""
        scheduler = EarliestDeadlineFirstVariant2(
            taskset=taskset,
            assignment=assignment, 
            number_of_cores=self.number_of_cores,
            start_time=6,
            finish_time=20
        )
        schedule, successfully_scheduled = scheduler.schedule()
        scheduler_name = self.scheduling_algorithms
        return schedule, successfully_scheduled, scheduler_name
    
    def _dm_scheduling(self, taskset, assignment):
        """Performs DM scheduling."""
        scheduler = DeadlineMonotonic(
            taskset=taskset,
            assignment=assignment,
            number_of_cores=self.number_of_cores,
            start_time=6,
            finish_time=20
        )
        schedule, successfully_scheduled = scheduler.schedule()
        scheduler_name = self.scheduling_algorithms
        return schedule, successfully_scheduled, scheduler_name

    def _dm_v1_scheduling(self, taskset, assignment):
        """Performs DM V1 scheduling."""
        scheduler = DeadlineMonotonicVariant1(
            taskset=taskset,
            assignment=assignment,
            number_of_cores=self.number_of_cores,
            start_time=6,
            finish_time=20
        )
        schedule, successfully_scheduled = scheduler.schedule()
        scheduler_name = self.scheduling_algorithms
        return schedule, successfully_scheduled, scheduler_name
    
    def _dm_v2_scheduling(self, taskset, assignment):
        """Performs DM V2 scheduling."""
        scheduler = DeadlineMonotonicVariant2(
            taskset=taskset,
            assignment=assignment,
            number_of_cores=self.number_of_cores,
            start_time=6,
            finish_time=20
        )
        schedule, successfully_scheduled = scheduler.schedule()
        scheduler_name = self.scheduling_algorithms
        return schedule, successfully_scheduled, scheduler_name
    
    def _combined_scheduling(self, taskset, assignment):
        """Performs Combined scheduling."""
        scheduler = CombinedScheduler(
            taskset=taskset,
            assignment=assignment, 
            number_of_cores=self.number_of_cores
        )
        schedule, successfully_scheduled = scheduler.schedule()
        scheduler_name = self.scheduling_algorithms
        return schedule, successfully_scheduled, scheduler_name
    


