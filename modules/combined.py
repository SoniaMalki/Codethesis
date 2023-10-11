import math
import logging
import numpy 
import time
from modules.homogeneous_scheduler import HomogeneousScheduler
from modules.earliest_deadline_first import EarliestDeadlineFirst
from modules.deadline_monotonic import DeadlineMonotonic
from modules.schedule_plan import SchedulePlan

class Combined:
    def __init__(self):
        self.algorithm_list = ["EDF", "EDFV1", "DM", "DMV1"]

    def schedule(self, busy_period_list, number_of_cores, assignment):
        combined_schedule_plan = SchedulePlan(number_of_cores)
        for busy_period in busy_period_list: #ca serait bien d'avoir un genre de liste avec des sous liste de début et de fin
            start_time = busy_period[0] #ex 25
            finish_time = busy_period[1]+1 #ex 30
            schedule_plan_all_algorithms=[]
            for algorithm in self.algorithm_list :
                scheduler = HomogeneousScheduler(assignment, algorithm, number_of_cores, start_time, finish_time)
                schedule_plan, successfully_scheduled, total_interference = scheduler.schedule()
                schedule_plan_all_algorithms.append([algorithm, schedule_plan, successfully_scheduled, total_interference])

            algorithm, schedule_plan, successfully_scheduled = self.choose_algorithm_with_minimum_interference(schedule_plan_all_algorithms)
            if not successfully_scheduled:
                return SchedulePlan(number_of_cores), 0

            combined_schedule_plan + schedule_plan
        return combined_schedule_plan, 1

    def choose_algorithm_with_minimum_interference(self, schedule_plan_list):
        minimum_schedule_plan_inteference_index = 0
        for index, schedule_plan in enumerate(schedule_plan_list):
            if schedule_plan[3] < schedule_plan_list[minimum_schedule_plan_inteference_index][3]:
                minimum_schedule_plan_inteference_index = index

        algorithm = schedule_plan_list[minimum_schedule_plan_inteference_index][0]
        schedule_plan = schedule_plan_list[minimum_schedule_plan_inteference_index][1]
        successfully_scheduled = schedule_plan_list[minimum_schedule_plan_inteference_index][2]
        return algorithm, schedule_plan, successfully_scheduled


