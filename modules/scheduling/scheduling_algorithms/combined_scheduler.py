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
    def __init__(self, taskset, assignment, number_of_cores, start_time=0, end_time=None):
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.assignment = assignment
        self.number_of_cores = number_of_cores
        if end_time == None:
            end_time = self.hyperperiod
        
        self.start_time = start_time
        self.end_time = end_time        
        
        self.schedulers = [
            EarliestDeadlineFirstVariant1,
            EarliestDeadlineFirstVariant2,
            DeadlineMonotonic,
            DeadlineMonotonicVariant1,
            DeadlineMonotonicVariant2,
        ]  # Sans EDF car cas par défaut

        # EDF par défaut
        self.edf_schedule = self.generate_scheduling(scheduler_class=EarliestDeadlineFirst, start_time=self.start_time, end_time=self.end_time)
        self.busy_periods = BusyPeriodGenerator.generate_busy_periods(self.edf_schedule)

    def __str__(self):
        return self.__class__.__name__

    def schedule(self):
        if not self.edf_schedule.success:
            print("Failed to schedule with EDF")
            return [], 0
        
        for busy_period_index in range(len(self.busy_periods)):  
            shortest_busy_period_length = len(self.busy_periods[busy_period_index]) 
            
            best_scheduling = self.busy_periods[busy_period_index]

            for scheduler_class in self.schedulers:
                scheduling = self.generate_scheduling(scheduler_class=scheduler_class, start_time=self.busy_periods[busy_period_index].start_time, end_time=self.busy_periods[busy_period_index].end_time + 1)
                scheduling_len = BusyPeriodGenerator.generate_scheduling_length(scheduling=scheduling)

                if scheduling.success:
                    if scheduling_len < shortest_busy_period_length:
                        shortest_busy_period_length = scheduling_len
                        best_scheduling = scheduling
            

            self.busy_periods[busy_period_index] = best_scheduling

        final_busy_period = BusyPeriod()
        for busy_period_index, busy_period in enumerate(self.busy_periods):
            shorter_busy_period = BusyPeriodGenerator.generate_busy_periods(scheduling=busy_period)
            for bp in shorter_busy_period:
                final_busy_period.add_period(scheduling=bp)
        return final_busy_period


    def generate_scheduling(self, scheduler_class, start_time=0, end_time=None):
        scheduler = scheduler_class(
                    taskset=self.taskset,
                    assignment=self.assignment,
                    number_of_cores=self.number_of_cores,
                    start_time=start_time,
                    end_time=end_time,
                )
        schedule, success = scheduler.schedule()
        return Scheduling(schedule=schedule, success=success, scheduler_name=str(scheduler))
