import numpy
import math
import time

class Wfdu:
    def __init__(self, _taskset ,_number_of_cores, _sorting_criterion):
        self.m = _number_of_cores
        self.taskset =_taskset
        self.period = self.taskset.period
        self.wcet = self.taskset.wcet
        self.sorting_criterion = _sorting_criterion
        print(self.m, self.period, self.wcet)

    def assign(self):
        print("test")
        taskset = self.sort_task(self.period, self.wcet)
        print("test2")
        taskset_na = taskset[:]
        taskAssigned = 1 #flag qui est a true tant que l'algo a réussi a assigner au moins une tâche a un core, une fois qu'il arrive pas ça sera 0
        taskincore = [[] for _ in range(self.m)]
        while taskset_na and taskAssigned == 1: #tant que soit on arrive encore a assigner et que le set des tâches à assigner n'est pas vide (il reste donc des tâches à assigner)
            taskset_na, taskAssigned, taskincore = self.task_partition(taskset_na, self.m, taskincore)
            print(taskset_na, taskAssigned, taskincore)
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
        taskset = sorted(list(range(len(ratio))), key=lambda k: ratio[k], reverse=True)
        time.sleep(2)
        return taskset

    def task_partition(self, taskset_na, m, taskincore):
        taskAssigned = 0 # Commence avec l'assomption qu'aucune tâche n'est assignée

        core_utilization = [sum([self.wcet[task] / self.period[task] for task in core]) for core in taskincore]

        # Parcourir les tâches dans l'ordre spécifié, en essayant de les assigner à un cœur
        for task in taskset_na:
            task_util = self.wcet[task] / self.period[task]

            # Trouver le cœur avec l'utilisation la plus faible
            min_utilization = math.inf  # On commence par l'infini pour s'assurer que le premier cœur vérifié aura une utilisation inférieure
            min_core_index = None

            for i, util in enumerate(core_utilization):
                if util + task_util <= 1 and util < min_utilization:  # 1 représente 100% d'utilisation
                    min_utilization = util
                    min_core_index = i

            # Si un cœur a été trouvé pour la tâche, assignez la tâche à ce cœur
            if min_core_index is not None:
                taskincore[min_core_index].append(task)
                core_utilization[min_core_index] += task_util  # Mettre à jour l'utilisation du cœur
                taskAssigned = 1  # Une tâche a été assignée
            else:
                break  # Si aucune tâche ne peut être assignée, sortir de la boucle

        # Mettre à jour taskset_na pour supprimer les tâches qui ont été assignées
        tasks_assigned = [task for core in taskincore for task in core]
        taskset_na = [task for task in taskset_na if task not in tasks_assigned]

        return taskset_na, taskAssigned, taskincore

    