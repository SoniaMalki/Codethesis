import time
from modules.scheduling.scheduling import Scheduling
from modules.scheduling.scheduling_algorithms.earliest_deadline_first import EarliestDeadlineFirst
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant1 import EarliestDeadlineFirstVariant1
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant2 import EarliestDeadlineFirstVariant2
from modules.scheduling.scheduling_algorithms.deadline_monotonic import DeadlineMonotonic
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant1 import DeadlineMonotonicVariant1
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant2 import DeadlineMonotonicVariant2
from modules.utils.busy_period import BusyPeriod
from modules.utils.busy_period_generator import BusyPeriodGenerator


class CombinedScheduler:
    def __init__(self, taskset, assignment, number_of_cores, scheduling_options, start_time=1, end_time=None):
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.assignment = assignment
        self.number_of_cores = number_of_cores
        self.scheduling_options = scheduling_options
        if end_time == None:
            end_time = self.hyperperiod

        self.start_time = start_time
        self.end_time = end_time

        self.schedulers = [
            EarliestDeadlineFirst,
            EarliestDeadlineFirstVariant1,
            EarliestDeadlineFirstVariant2,
            DeadlineMonotonic,
            DeadlineMonotonicVariant1,
            DeadlineMonotonicVariant2,
        ]

        self.total_utilization = None
        self.actual_utilization = None
        # Find the scheduling by default
        default_scheduler_class_success = 0
        default_scheduler_class_index = 0

        while not default_scheduler_class_success and default_scheduler_class_index < len(self.schedulers):
            default_scheduler_class = self.schedulers[default_scheduler_class_index]
            self.default_schedule = self.generate_scheduling(
                scheduler_class=default_scheduler_class, start_time=self.start_time, end_time=self.end_time)
            default_scheduler_class_success = self.default_schedule.success

            if default_scheduler_class_success:
                self.schedulers = self.schedulers[default_scheduler_class_index+1:]

            default_scheduler_class_index += 1

        self.busy_periods = BusyPeriodGenerator.generate_busy_periods(
            self.default_schedule)

        # self.total_utilization = []
        # self.actual_utilization = []

    def __str__(self):
        return self.__class__.__name__

    def schedule(self):
        if not self.default_schedule.success:
            print(
                "Failed to schedule with all the schedulers. CombinedScheduler will return empty Scheduling for the whole period")
            return self.create_empty_return()

        for busy_period_index in range(len(self.busy_periods)):
            shortest_busy_period_length = len(
                self.busy_periods[busy_period_index])

            best_scheduling = self.busy_periods[busy_period_index]

            for scheduler_class in self.schedulers:
                scheduling = self.generate_scheduling(
                    scheduler_class=scheduler_class, start_time=self.busy_periods[busy_period_index].start_time, end_time=self.busy_periods[busy_period_index].end_time)
                scheduling_len = BusyPeriodGenerator.generate_scheduling_length(
                    scheduling=scheduling)

                if scheduling.success:
                    if scheduling_len < shortest_busy_period_length:
                        shortest_busy_period_length = scheduling_len
                        best_scheduling = scheduling

            self.busy_periods[busy_period_index] = best_scheduling

        final_busy_period = BusyPeriod()
        for busy_period_index, busy_period in enumerate(self.busy_periods):
            shorter_busy_period = BusyPeriodGenerator.generate_busy_periods(
                scheduling=busy_period)
            for bp in shorter_busy_period:
                final_busy_period.add_period(scheduling=bp)
                if bp.total_utilization is not None:
                    if self.total_utilization is None:
                        self.total_utilization = []
                    self.total_utilization.append(bp.total_utilization)

        if self.total_utilization is not None:
            self.actual_utilization = [
                t_u/self.hyperperiod for t_u in self.total_utilization]
        else:
            self.actual_utilization = None

        return final_busy_period

    def generate_scheduling(self, scheduler_class, start_time=1, end_time=None):
        scheduler = scheduler_class(
            taskset=self.taskset,
            assignment=self.assignment,
            number_of_cores=self.number_of_cores,
            scheduling_options=self.scheduling_options,
            start_time=start_time,
            end_time=end_time,
        )
        schedule, success = scheduler.schedule()
        return Scheduling(
            schedule=schedule, success=success, scheduler_name=str(scheduler))

    def create_empty_return(self):
        scheduling = [[] for _ in range(self.number_of_cores)]
        for core in scheduling:
            core.append((1, None, None))
            core.append((self.end_time, None, None))
        empty_scheduling = Scheduling(
            schedule=scheduling, success=0, scheduler_name="N/A")

        empty_busy_period = BusyPeriod()
        empty_busy_period.add_period(empty_scheduling)
        return empty_busy_period
