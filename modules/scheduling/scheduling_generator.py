from time import perf_counter

import numpy

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
    def __init__(self, taskset_set_obj, assignment_set_obj, taskset_id, assignment_id, scheduling_id, scheduling_algorithm, scheduling_options):
        print("Initializing SchedulingGenerator")
        self.taskset_set = taskset_set_obj
        self.assignment_set = assignment_set_obj
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_id = scheduling_id
        self.scheduling_algorithm = scheduling_algorithm
        self.scheduling_options = scheduling_options
        self.number_of_cores = self.assignment_set.number_of_cores
        self.scheduling_algorithms = [
            "EarliestDeadlineFirst",
            "EarliestDeadlineFirstVariant1",
            "EarliestDeadlineFirstVariant2",
            "DeadlineMonotonic",
            "DeadlineMonotonicVariant1",
            "DeadlineMonotonicVariant2"
        ]

        self.composite_scheduling_algorithms = [
            "CombinedScheduler",
            "Rhma"
        ]
        print(
            f"SchedulingGenerator initialized with algorithm: {self.scheduling_algorithm}")

    def generate_scheduling_set(self):
        """Generates schedulings for each assignment within the TasksetSet."""
        print("Generating scheduling set")
        scheduling_list = []  # Store schedulings for each assignment

        # Determine the scheduling algorithm once
        if self.scheduling_algorithm not in self.scheduling_algorithms and self.scheduling_algorithm not in self.composite_scheduling_algorithms:
            print(
                f"Invalid scheduling algorithm: {self.scheduling_algorithm}. Returning None.")
            return None

        scheduler_class = globals()[self.scheduling_algorithm]

        if self.scheduling_algorithm in self.scheduling_algorithms:
            scheduling_function = self.generate_scheduling
        else:
            scheduling_function = self.generate_composite_scheduling

        # Apply the selected scheduling function to all taskset assignments
        for taskset, assignment in zip(self.taskset_set, self.assignment_set):
            if assignment.success:
                print(
                    f"Generating scheduling for taskset: {taskset.taskset_id} and assignment: {assignment.assignment_id}")
                scheduling = scheduling_function(
                    taskset=taskset, assignment=assignment, scheduler_class=scheduler_class, start_time=1, end_time=None)
                scheduling_list.append(scheduling)
                print(
                    f"Scheduling generated for taskset: {taskset.taskset_id} and assignment: {assignment.assignment_id}")

        scheduling = SchedulingSet(scheduling_id=self.scheduling_id, taskset_id=self.taskset_id, assignment_id=self.assignment_id,
                                   scheduling_algorithm=self.scheduling_algorithm, scheduling_options=self.scheduling_options, scheduling_list=scheduling_list)
        print("Scheduling set generation completed")
        return scheduling

    def generate_scheduling(self, taskset, assignment, scheduler_class, start_time=1, end_time=None):
        print(f"Generating scheduling using {scheduler_class.__name__}")
        start_time_compute = perf_counter()
        scheduler = scheduler_class(
            taskset=taskset,
            assignment=assignment,
            number_of_cores=self.number_of_cores,
            scheduling_options=self.scheduling_options,
            start_time=start_time,
            end_time=end_time,
        )
        schedule, success = scheduler.schedule()
        end_time_compute = perf_counter()
        computation_time = end_time_compute - start_time_compute
        if not success:
            computation_time = numpy.nan
            actual_utilization = numpy.nan
            theoritical_utilization = numpy.nan
            print(
                f"Scheduling failed for taskset: {taskset.taskset_id} and assignment: {assignment.assignment_id}")
        else:
            actual_utilization = scheduler.actual_utilization
            theoritical_utilization = sum(taskset.utilization)
            print(
                f"Scheduling succeeded for taskset: {taskset.taskset_id} and assignment: {assignment.assignment_id}")

        scheduling = Scheduling(
            schedule=schedule, success=success, scheduler_name=str(scheduler))
        scheduling.add_performances(
            computation_time=computation_time, actual_utilization=actual_utilization, theoritical_utilization=theoritical_utilization)
        return scheduling

    def generate_composite_scheduling(self, taskset, assignment, scheduler_class, start_time=1, end_time=None):
        print(
            f"Generating composite scheduling using {scheduler_class.__name__}")
        start_time_compute = perf_counter()
        scheduler = scheduler_class(
            taskset=taskset,
            assignment=assignment,
            number_of_cores=self.number_of_cores,
            scheduling_options=self.scheduling_options,
            start_time=start_time,
            end_time=end_time
        )
        busy_periods = scheduler.schedule()
        end_time_compute = perf_counter()
        computation_time = end_time_compute - start_time_compute

        scheduling = CompositeScheduling(scheduler_name=str(scheduler))
        for busy_period in busy_periods:
            scheduling.add_schedule(schedule=busy_period)

        if not scheduling.success:
            computation_time = numpy.nan
            actual_utilization = numpy.nan
            theoritical_utilization = numpy.nan
            print(
                f"Composite scheduling failed for taskset: {taskset.taskset_id} and assignment: {assignment.assignment_id}")
        else:
            actual_utilization = sum(scheduler.actual_utilization)
            theoritical_utilization = sum(taskset.utilization)
            print(
                f"Composite scheduling succeeded for taskset: {taskset.taskset_id} and assignment: {assignment.assignment_id}")

        scheduling.add_performances(
            computation_time=computation_time, actual_utilization=actual_utilization, theoritical_utilization=theoritical_utilization)
        return scheduling
