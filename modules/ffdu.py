import numpy
import math
from pulp import *
import time

class Ffdu:
    def __init__(self, _taskset ,_number_of_cores, _sorting_criterion):
        self.m = _number_of_cores
        self.taskset =_taskset
        self.period = self.taskset.period
        self.wcet = self.taskset.wcet
        self.sorting_criterion = _sorting_criterion
        self.interference = self.taskset.interference
        pass
    def assign(self):
        #Algorithme de CITTA
        taskset = self.sort_task(self.period, self.wcet, self.interference, self.sorting_criterion)
        taskset_na = taskset[:]
        taskAssigned = 1 #flag qui est a true tant que l'algo a réussi a assigner au moins une tâche a un core, une fois qu'il arrive pas ça sera 0
        taskincore = [[] for _ in range(self.m)]
        while taskset_na and taskAssigned == 1: #tant que soit on arrive encore a assigner et que le set des tâches à assigner n'est pas vide (il reste donc des tâches à assigner)
            taskset_na, taskAssigned, taskincore = self.task_partition(taskset_na, self.m, taskincore, self.period, self.wcet, self.interference)
        # print "TaskIncore is ",taskincore
        if not taskset_na:
            return taskincore, taskset_na, 1
        else:
            return taskincore, taskset_na, 0