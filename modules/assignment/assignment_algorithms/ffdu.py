import numpy
import math
import time

class Ffdu:
    def __init__(self, taskset, number_of_cores):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.period = self.taskset.period
        self.wcet = self.taskset.wcet
        self.utilization = self.taskset.utilization
        self.interference = self.taskset.interference

    def assign(self):
        taskset = sorted(range(len(self.utilization)), key=lambda k: self.utilization[k], reverse=True)
        task_in_core = [[] for _ in range(self.number_of_cores)]
        taskset_not_assigned = taskset[:]

        successfully_assigned = 1
        while taskset_not_assigned and successfully_assigned == 1:
            task_in_core, taskset_not_assigned, successfully_assigned = self.task_partition(task_in_core=task_in_core, taskset_not_assigned=taskset_not_assigned)

        if not taskset_not_assigned:
            return task_in_core, 1
        else:
            return task_in_core, 0

    def task_partition(self, task_in_core, taskset_not_assigned):
        successfully_assigned = 0
        task_not_assigned = []
        for task_index in taskset_not_assigned:  
            core_found = False
            for core_index in range(self.number_of_cores):
                if self.check_task_fit(task_index, core_index, task_in_core):
                    task_in_core[core_index].append(task_index)
                    successfully_assigned = 1
                    core_found = True
                    break
            if not core_found:
                task_not_assigned.append(task_index)
                
        return task_in_core, task_not_assigned, successfully_assigned

    def check_task_fit(self, task_index, core_index, task_in_core):
        total_utilization = sum(
            self.utilization[task] for task in task_in_core[core_index]
        )
        if total_utilization + self.utilization[task_index] <= 1:
            return True
        else:
            return False