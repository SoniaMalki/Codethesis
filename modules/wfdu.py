import numpy
import math
from pulp import *
import time

class Wfdu:
    def __init__(self, _taskset ,_number_of_cores, _sorting_criterion):
        self.m = _number_of_cores
        self.taskset =_taskset
        self.period = self.taskset.period
        self.wcet = self.taskset.wcet
        self.sorting_criterion = _sorting_criterion

    def assign(self):
        taskset = self.sort_task(self.period, self.wcet)
        taskset_na = taskset[:]
        taskAssigned = 1 #flag qui est a true tant que l'algo a réussi a assigner au moins une tâche a un core, une fois qu'il arrive pas ça sera 0
        taskincore = [[] for _ in range(self.m)]
        while taskset_na and taskAssigned == 1: #tant que soit on arrive encore a assigner et que le set des tâches à assigner n'est pas vide (il reste donc des tâches à assigner)
            taskset_na, taskAssigned, taskincore = self.task_partition(taskset_na, self.m, taskincore)
        # print "TaskIncore is ",taskincore
        if not taskset_na:
            return taskincore, taskset_na, 1
        else:
            return taskincore, taskset_na, 0

    def sort_task(self, p, c):
        #Trie les tâches par ordre décroissant selon certains critère. Ca regarde le critère, imaginons 
        # deadline=[33,10,21] et ça donne l'ordre des tâches selon ça, donc tâche avec plus grande deadline
        # jusque la tâche avec la plus petite deadline, donc ici taskset=[0,2,1] 
        # trier selon le ratio WCET/T, donc l'utilisation
        per = numpy.array(p, dtype='f')
        ec = numpy.array(c, dtype='f')
        ratio = ec / per
        print(ratio)
        taskset = sorted(list(range(len(ratio))), key=lambda k: ratio[k], reverse=True)
        print(taskset)
        time.sleep(10)
        return taskset

    def task_partition(self, taskset_na, m, taskincore):
        taskAssigned = 0

        # PuLP variables and model
        prob = LpProblem("WFDU_Task_Partitioning", LpMaximize)
        task_vars = LpVariable.dicts("Task", taskset_na, 0, 1, LpBinary)

        # Objective: Maximize the worst-fit core utilization
        prob += lpSum([task_vars[i] for i in taskset_na])

        # Constraints
        for i in range(m):
            prob += lpSum([self.wcet[j] * task_vars[j] for j in taskset_na]) <= self.period[i]

        # Solve the problem
        prob.solve()

        # Assign tasks to cores based on the solution
        for i in taskset_na:
            if task_vars[i].varValue == 1:
                for core_index, core in enumerate(taskincore):
                    if sum(self.wcet[j] for j in core) + self.wcet[i] <= self.period[core_index]:
                        core.append(i)
                        taskAssigned = 1
                        break

        # Remove assigned tasks from taskset_na
        taskset_na = [i for i in taskset_na if i not in sum(taskincore, [])]

        return taskset_na, taskAssigned, taskincore

    