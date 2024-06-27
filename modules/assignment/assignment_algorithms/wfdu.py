import numpy
import math
import time

class Wfdu:
    def __init__(self, taskset, number_of_cores):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.period = self.taskset.period
        self.wcet = self.taskset.wcet
        self.utilization = self.taskset.utilization
        self.interference = self.taskset.interference


    def assign(self):
        taskset = sorted(range(len(self.utilization)), key=lambda k: self.utilization[k], reverse=True)
        print(taskset)
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
            core_index = self.find_worst_fit_core(task_in_core, task_index)
            if core_index is not None:
                task_in_core[core_index].append(task_index)
                successfully_assigned = 1
            else:
                task_not_assigned.append(task_index)
        return task_in_core, task_not_assigned, successfully_assigned

    def find_worst_fit_core(self, task_in_core, task_index):
        """Trouve le cœur avec l'utilisation la plus élevée (pour WFDU) et vérifie la limite d'utilisation."""
        min_utilization = 1
        worst_fit_core = None
        for core_index in range(self.number_of_cores):
            total_utilization = sum(
                self.utilization[task] for task in task_in_core[core_index]
            )
            # Vérifie si la tâche rentre dans la limite d'utilisation du cœur
            print(min_utilization, total_utilization, core_index, task_index)
            if total_utilization + self.utilization[task_index] <= 1 and total_utilization < min_utilization:
                min_utilization = total_utilization
                worst_fit_core = core_index
        print(f"assign {task_index} in {worst_fit_core}")
        return worst_fit_core
    
