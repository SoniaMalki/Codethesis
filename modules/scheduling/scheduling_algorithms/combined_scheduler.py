import time
from modules.scheduling.scheduling import Scheduling
from modules.scheduling.scheduling_algorithms.earliest_deadline_first import EarliestDeadlineFirst
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant1 import EarliestDeadlineFirstVariant1
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant2 import EarliestDeadlineFirstVariant2
from modules.scheduling.scheduling_algorithms.deadline_monotonic import DeadlineMonotonic
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant1 import DeadlineMonotonicVariant1
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant2 import DeadlineMonotonicVariant2
from modules.utils.busy_period_generator import BusyPeriodGenerator

class CombinedScheduler:
    def __init__(self, taskset, assignment, number_of_cores):
        self.taskset = taskset
        self.assignment = assignment
        self.number_of_cores = number_of_cores
        self.schedulers = [
            EarliestDeadlineFirstVariant1,
            EarliestDeadlineFirstVariant2,
            DeadlineMonotonic,
            DeadlineMonotonicVariant1,
            DeadlineMonotonicVariant2,
        ]  # Sans EDF car cas par défaut

        # EDF par défaut
        self.final_schedule = self.generate_scheduling(scheduler_class=EarliestDeadlineFirst)
        self.busy_periods = BusyPeriodGenerator.generate_busy_periods(self.final_schedule)

    def __str__(self):
        return self.__class__.__name__

    def schedule(self):
        if not self.final_schedule.success:
            print("Failed to schedule with EDF")
            return [], 0
        
        for busy_period_index in range(len(self.busy_periods)):  
            shortest_busy_period_length = len(self.busy_periods[busy_period_index]) 
            print(f"shortest bp length initial: {shortest_busy_period_length}") 
            
            best_scheduling = self.busy_periods[busy_period_index]
            print(type(best_scheduling))
            print(f"best schedule : {best_scheduling}; best sch name: {best_scheduling.scheduler_name}")

            for scheduler_class in self.schedulers:
                scheduling = self.generate_scheduling(scheduler_class=scheduler_class, start_time=self.busy_periods[busy_period_index].start_time, finish_time=self.busy_periods[busy_period_index].end_time + 1)
                scheduling = BusyPeriodGenerator.generate_shorter_scheduling(scheduling=scheduling)
                if scheduling.success:
                    busy_period_length = len(scheduling[0]) 
                    print(f'busy_period_length: {busy_period_length}, shortest_busy_period_lenght: {shortest_busy_period_length}')
                    if busy_period_length < shortest_busy_period_length:
                        shortest_busy_period_length = busy_period_length
                        best_scheduling = scheduling
            print(f"best_schedule:{best_scheduling}, best_schedule name:{best_scheduling.scheduler_name}")

            self.busy_periods[busy_period_index] = best_scheduling

        return self.busy_periods, 1 


    def generate_scheduling(self, scheduler_class, start_time=0, finish_time=None):
        scheduler = scheduler_class(
                    taskset=self.taskset,
                    assignment=self.assignment,
                    number_of_cores=self.number_of_cores,
                    start_time=start_time,
                    finish_time=finish_time,
                )
        print(f"scheduler name: {scheduler}")
        schedule, success = scheduler.schedule()
        return Scheduling(schedule=schedule, success=success, scheduler_name=str(scheduler))
