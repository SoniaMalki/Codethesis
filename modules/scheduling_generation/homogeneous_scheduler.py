import math
import logging
import numpy 
import time
from modules.scheduling_generation.earliest_deadline_first import EarliestDeadlineFirst
from modules.scheduling_generation.earliest_deadline_first_variant1 import EarliestDeadlineFirstVariant1
from modules.scheduling_generation.deadline_monotonic import DeadlineMonotonic
from modules.scheduling_generation.deadline_monotonic_variant1 import DeadlineMonotonicVariant1
from modules.scheduling_generation.schedule_plan import SchedulePlan
from itertools import chain

class HomogeneousScheduler:
    def __init__(self, _assignment, _scheduling_algorithm_name, _number_of_cores, _start_time=0, _end_time=0):
        self.assignment = _assignment
        self.number_of_cores = _number_of_cores
        self.scheduling_algorithm_name = _scheduling_algorithm_name
        if self.scheduling_algorithm_name.lower() == "edf":
            self.scheduling_algorithm = EarliestDeadlineFirst()
        elif self.scheduling_algorithm_name.lower() == "edfv1":
            self.scheduling_algorithm = EarliestDeadlineFirstVariant1()
        elif self.scheduling_algorithm_name.lower() == "dm":
            self.scheduling_algorithm = DeadlineMonotonic()
        elif self.scheduling_algorithm_name.lower() == "dmv1":
            self.scheduling_algorithm = DeadlineMonotonicVariant1()
        self.taskset = self.assignment["taskset"]
        self.taskset_assignment = self.assignment["taskset_assignment"]
        self.start_time = _start_time
        self.end_time = _end_time
        if self.end_time == 0:
            self.end_time = self.ppcm()


    def schedule(self):
        w_matrix = [[0 for _ in range(len(self.taskset))]  for _ in range(len(self.taskset))]
        schedule_plan_total = SchedulePlan(self.number_of_cores)
        schedule_plan = [[] for core in range(self.number_of_cores)]
        scheduler = self.scheduling_algorithm 
        total_interference = 0

        for task in self.taskset:
            task.create_jobs(self.start_time, self.end_time)

        current_time = self.start_time

        running_task_list = [None for core in range(self.number_of_cores)]
        current_task_list = [None for core in range(self.number_of_cores)]
        while current_time < self.end_time:
            for k, tasks_in_core in enumerate(self.taskset_assignment): #loop for updating priority
                scheduler.updateStatus(current_time, tasks_in_core)
                running_task_list[k] = scheduler.updatepriority(current_time, tasks_in_core, k, running_task_list[k]) #teta stocked in here
            
            #beginning of the part that calculate the interference
            for k, tasks_in_core in enumerate(self.taskset_assignment): #loop for updating the interference matrix W
                if running_task_list[k] != None:
                    if running_task_list[k] != current_task_list[k] and current_time % running_task_list[k].period == 0 : #if there is a context switch (running task is not the same as current_task) & activation time (because %period ==0)
                        for s in range(len(self.taskset_assignment)): #we will explore the other tasks on other core it this is the case
                            if s != k and sum(running_task_list[k].interference) > 0 : #if the core is another one and the inteference of the job is 1 (it will receive inteference), we will check which task broadcast this interference
                                if running_task_list[s] != None:
                                    w_matrix[s][k] = 1 #set the matrix to 1
                                    running_task_list[k].remaining_execution_time += running_task_list[s].interference #augment their wcet, by the interference of the task 
                                    total_interference += 1
                    else: #for other case other than activation or context switch, we will refer to the W matrix
                        for s in range(len(self.taskset_assignment)):
                            if s != k and sum(running_task_list[k].interference) > 0:
                                if running_task_list[s] != None:
                                    if w_matrix[s][k] == 0:
                                        w_matrix[s][k] = 1
                                        running_task_list[k].remaining_execution_time += running_task_list[s].interference
                                        total_interference += 1

            for core_number, tasks_in_core in enumerate(self.taskset_assignment): #loop for executing each core
                current_task_list[core_number] = running_task_list[core_number]
                execution = scheduler.execute(current_time, core_number, current_task_list[core_number])
                schedule_plan[core_number].append(execution)
                if current_task_list[core_number] != None:
                    if current_task_list[core_number].remaining_execution_time == 0 : #if job is finished
                        for j in range(len(self.taskset)):
                            w_matrix[j][core_number] = 0
                            w_matrix[core_number][j] = 0
            current_time += 1
            


        if current_time == self.end_time:
            for core_index, core in enumerate(schedule_plan):
                schedule_plan_total.add_core_scheduling(core_index, core, self.scheduling_algorithm_name)
            print(schedule_plan_total)
            return schedule_plan_total, 1, total_interference
    

    


    def ppcm(self):
        array_numpy = self.taskset.period
        array_entiers = (array_numpy * 10).astype(int)
        ppcm = numpy.lcm.reduce(array_entiers)
        if ppcm % 10 == 0:
            ppcm /= 10
            ppcm = int(ppcm)

        return ppcm


