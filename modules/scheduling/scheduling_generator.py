from modules.scheduling.scheduling import Scheduling
from modules.scheduling.composite_scheduling import CompositeScheduling
from modules.scheduling.scheduling_set import SchedulingSet

from modules.scheduling.scheduling_algorithms.combined_scheduler import CombinedScheduler
from modules.scheduling.scheduling_algorithms.rhma import Rhma

from modules.scheduling.scheduling_algorithms.earliest_deadline_first import EarliestDeadlineFirst
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant1 import EarliestDeadlineFirstVariant1
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant2 import EarliestDeadlineFirstVariant2
from modules.scheduling.scheduling_algorithms.deadline_monotonic import DeadlineMonotonic
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant1 import DeadlineMonotonicVariant1
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant2 import DeadlineMonotonicVariant2

import time

class SchedulingGenerator:
    def __init__(self, taskset_set_obj, assignment_set_obj, taskset_id, assignment_id, scheduling_id, scheduling_algorithms):
        self.taskset_set = taskset_set_obj
        self.assignment_set = assignment_set_obj
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_id = scheduling_id
        self.scheduling_algorithms = scheduling_algorithms[0]
        self.number_of_cores = self.assignment_set.number_of_cores

    def get_class_by_name(self, class_name):
        return globals()[class_name]

    def generate_scheduling_set(self):
        """Generates schedulings for each assignment within the TasksetSet."""

        scheduling_list = []  # Store schedulings for each assignment
        scheduling_algorithms = [
            "EarliestDeadlineFirst",
            "EarliestDeadlineFirstVariant1",
            "EarliestDeadlineFirstVariant2",
            "DeadlineMonotonic",
            "DeadlineMonotonicVariant1",
            "DeadlineMonotonicVariant2"
        ]
        composite_scheduling_algorithms = [
            "CombinedScheduler",
            "Rhma"
        ]
        # Determine the scheduling algorithm once
        if self.scheduling_algorithms not in scheduling_algorithms and self.scheduling_algorithms not in composite_scheduling_algorithms:
            print(f"Invalid scheduling algorithm: {self.scheduling_algorithms}. Returning None.")
            return None
        
        else: 
            scheduler_class = self.get_class_by_name(class_name=self.scheduling_algorithms)
            if self.scheduling_algorithms in scheduling_algorithms:
                scheduling_function = self.generate_scheduling
            else:
                scheduling_function = self.generate_composite_scheduling

        # Apply the selected scheduling function to all taskset assignments
        for taskset, assignment in zip(self.taskset_set, self.assignment_set):
            if assignment.success: 
                scheduling = scheduling_function(taskset=taskset, assignment=assignment, scheduler_class=scheduler_class, start_time=0, end_time=None)
                scheduling_list.append(scheduling)    
                print(scheduling.__str__(end_time=None))     
                print(f'success: {scheduling.success}')

        scheduling = SchedulingSet(scheduling_id=self.scheduling_id, taskset_id=self.taskset_id, assignment_id=self.assignment_id, scheduling_algorithms=self.scheduling_algorithms, scheduling_list=scheduling_list)  # Store assignments for each taskset
        return scheduling  

    def generate_scheduling(self, taskset, assignment, scheduler_class, start_time=0, end_time=None):
        scheduler = scheduler_class(
                    taskset=taskset,
                    assignment=assignment,
                    number_of_cores=self.number_of_cores,
                    start_time=start_time,
                    end_time=end_time,
                )
        schedule, success = scheduler.schedule()
        return Scheduling(schedule=schedule, success=success, scheduler_name=str(scheduler))

   
    def generate_composite_scheduling(self, taskset, assignment, scheduler_class, start_time=0, end_time=None):
        taskset.interference = [0,1,1,0]
        scheduler = scheduler_class(
            taskset=taskset,
            assignment=assignment, 
            number_of_cores=self.number_of_cores,
            start_time=start_time,
            end_time=end_time
        )
        busy_periods = scheduler.schedule()
        scheduling = CompositeScheduling(scheduler_name=str(scheduler))
        for busy_period in busy_periods:
            scheduling.add_schedule(schedule=busy_period)
        return scheduling
    


