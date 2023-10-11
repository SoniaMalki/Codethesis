import math
import logging
import numpy 
import time
from modules.homogeneous_scheduler import HomogeneousScheduler
from modules.earliest_deadline_first import EarliestDeadlineFirst
from modules.deadline_monotonic import DeadlineMonotonic
from modules.combined import Combined
from modules.rhma import Rhma
from modules.schedule_plan import SchedulePlan

class MixedScheduler:
    def __init__(self, _assignment, _scheduling_algorithm_name, _number_of_cores, _current_time=0):
        self.assignment = _assignment
        self.number_of_cores = _number_of_cores
        self.scheduling_algorithm_name = _scheduling_algorithm_name
        self.taskset = self.assignment["taskset"]
        self.taskset_assignment = self.assignment["taskset_assignment"]
        self.current_time = _current_time #TODO A VOIR 
        self.hyperperiod = self.ppcm()+_current_time
        self.algorithm_list = ["EDF", "EDFV1", "DM", "DMV1"]

    def schedule(self):
        busy_period_list = self.compute_busy_period()
        scheduler = Combined()
        combined_schedule_plan, successfully_scheduled = scheduler.schedule(busy_period_list, self.number_of_cores, self.assignment)
        busy_period_list = self.compute_busy_period(combined_schedule_plan, successfully_scheduled)
        scheduler = Rhma()
        rhma_schedule_plan, rhma_successfully_scheduled = scheduler.schedule(busy_period_list, self.number_of_cores, self.assignment, self.hyperperiod)
        return combined_schedule_plan, successfully_scheduled



    def compute_busy_period(self, schedule=None, successfully_scheduled=None):
        monocore_busy_period = []
        if schedule == None:
            scheduler = HomogeneousScheduler(self.assignment, "EDF", self.number_of_cores)
            schedule, successfully_scheduled, total_interference =  scheduler.schedule()

        if not successfully_scheduled:
            return []
        for core in schedule:
            monocore_busy_period.extend(self.monocore_busy_period(schedule[core]))
        busy_period = []

        for times in range(self.hyperperiod):  
            if times in monocore_busy_period:
                busy_period.append(times)
        busy_period = self.group_consecutive_numbers(busy_period)
        return busy_period
        
    def monocore_busy_period(self, core):
        res = []
        if len(core) != 0:
            for period in core:
                for time_execution in period["schedule_plan"]:   
                    if not time_execution.is_idle():
                        res.append(time_execution.time)
        return res


    def group_consecutive_numbers(self, numbers_list):
        res = []
        if len(numbers_list) != 0:
            current_group = [numbers_list[0]]

            for i in range(1, len(numbers_list)):
                if numbers_list[i]-numbers_list[i-1] == 1:
                    current_group.append(numbers_list[i])
                else:
                    res.append(current_group)
                    current_group = [numbers_list[i]]
            res.append(current_group)

            for i in range(len(res)):
                temp = [res[i][0], res[i][-1]]
                res[i] = temp
            
        return res


    def ppcm(self):
        array_numpy = self.taskset.period
        array_entiers = (array_numpy * 10).astype(int)
        ppcm = numpy.lcm.reduce(array_entiers)
        if ppcm % 10 == 0:
            ppcm /= 10
            ppcm = int(ppcm)

        return ppcm
