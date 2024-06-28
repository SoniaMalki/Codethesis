import numpy
import math
from pulp import *
import time

class Citta:
    def __init__(self, taskset , number_of_cores, sorting_criterion):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.period = self.taskset.period
        self.deadline = self.taskset.deadline
        self.wcet = self.taskset.wcet
        self.interference = self.taskset.interference
        self.utilization = self.taskset.utilization
        self.sorting_criterion = sorting_criterion

    def sort_task(self):
        #Trie les tâches par ordre décroissant selon certains critère. Ca regarde le critère, imaginons 
        # deadline=[33,10,21] et ça donne l'ordre des tâches selon ça, donc tâche avec plus grande deadline
        # jusque la tâche avec la plus petite deadline, donc ici taskset=[0,2,1] 
        taskset = list(range(len(self.period)))  # Create a list of task indices

        if self.sorting_criterion == "wcet_ascending":
            taskset = sorted(taskset, key=lambda k: self.wcet[k])
        elif self.sorting_criterion == "wcet_descending":
            taskset = sorted(taskset, key=lambda k: self.wcet[k], reverse=True)
        elif self.sorting_criterion == "period_ascending":
            taskset = sorted(taskset, key=lambda k: self.period[k])
        elif self.sorting_criterion == "period_descending":
            taskset = sorted(taskset, key=lambda k: self.period[k], reverse=True)
        elif self.sorting_criterion == "utilization_ascending":
            taskset = sorted(taskset, key=lambda k: self.utilization[k])
        elif self.sorting_criterion == "utilization_descending":
            taskset = sorted(taskset, key=lambda k: self.utilization[k], reverse=True)
        elif self.sorting_criterion == "execution_slack_ascending":
            taskset = sorted(taskset, key=lambda k: self.period[k] - self.wcet[k])
        elif self.sorting_criterion == "execution_slack_descending":
            taskset = sorted(taskset, key=lambda k: self.period[k] - self.wcet[k], reverse=True)
        elif self.sorting_criterion == "random_order":
            numpy.random.shuffle(taskset)  # Shuffle the list for random order
        else:
            print(f"Invalid sorting criterion: {self.sorting_criterion}. Returning tasks in random order.")
            numpy.random.shuffle(taskset)
        return taskset
    

    def assign(self):
        #Algorithme de CITTA
        taskset = self.sort_task()
        taskset_not_assigned = taskset[:]
        successfully_assigned = 1 #flag qui est a true tant que l'algo a réussi a assigner au moins une tâche a un core, une fois qu'il arrive pas ça sera 0
        task_in_core = [[] for _ in range(self.number_of_cores)]
        while taskset_not_assigned and successfully_assigned == 1: #tant que soit on arrive encore a assigner et que le set des tâches à assigner n'est pas vide (il reste donc des tâches à assigner)
            task_in_core, taskset_not_assigned, successfully_assigned = self.task_partition(taskset=taskset_not_assigned, task_in_core=task_in_core)
        # print "TaskIncore is ",taskincore
        if not taskset_not_assigned:
            return task_in_core, 1
        else:
            return task_in_core, 0

    def task_partition(self, taskset, task_in_core):
        #Essaie d'assigner des tâches à des cores
        successfully_assigned = 0 #flag pour dire qu'au moins une tâche est assignée de tout l'attempt. On commence à 0, et si c'est assigné au moins une fois
        #ça sera 1, et renverra 1, preuve que la boucle dans catpar qui l'appelle pourra encore tourner car encore possible d'assigner.
        task_not_assigned = [] #on assume que le set des tâches non assignée est vide au début et se remplit au fur des attempt.
        task_to_assign = taskset[:] 
        #attention tasket est le taskset des tâches à chercher a assigner. Au début il vaut le total, mais après vaut task_tna des attempts précédentes
        #taskreming est l'équivalent du taskset, sauf qu'on retire les attempt réussies. On peut pas le faire sur taskset directement vu qu'il y a 
        #une boucle dessus. Mais taskreming prend en compte les tâches assignées en les retirant, c'est le set des tâches à assigner qu'il reste et
        #des tâches qui sont données à task_tna. Utile pour calculer l'interférence, il n'est utilisé que là.
        #taskreming contient tout sauf les tasks qui sont successfly assigned.
        for task_index in taskset:
            assign_to = -1 # core par défaut si aucun core trouvé ça reste à -1 et à la fin du for, on sait si c'est assigné à un core ou aucun
            for core in range(self.number_of_cores): #on teste d'assigner la tache du taskset à chaque core m
                task_in_core[core].append(task_index) #ajout de la tâche au core pour pouvoir calculer l'interference et si elle fit. 
                wcet_with_interference = numpy.copy(self.wcet) #besoin d'un vecteur wcet_sc pour stocker les wcet avec interference qui seront calculées
                core_success = 1 #on suppose que l'attempt du schedule du core est correcte, pour après la refuser si ça ne va pas
                #si c'est accepté alors on la garde au core, sinon on la supprimera du core si l'attempt est refusé
                for task in task_in_core[core]:
                    #calculer le wcet + l'interference pour le taskset assigné au core qu'on test
                    wcet_with_interference[task] = self.compute_interference(task_index=task, core_index=core, task_in_core=task_in_core, task_to_assign=task_to_assign)
                for task in task_in_core[core]:
                    if self.check_one_task(task_index=task, core=task_in_core[core], wcet_with_interference=wcet_with_interference) == 0: #on teste la condition de schedule tache par tache sur le core, 
                        # en prenant en compte la nouvelle tache et les nouveau wcet calculés
                        task_in_core[core].remove(task_index) #si on rentre dans la boucle c'est qu'on a renvoyé 0, donc raté pour une seule tâche, on retire donc la nouvelle tâche ajoutée au core 
                        #car avant de l'avoir mis ça marchait, mais en l'ajoutant, ça ne marche plus. Donc c'est cette tâche le problème et on la retire
                        core_success = 0 #on dit que l'attempt de cette tâche à ce core m est fausse, et on va aller au core suivant pour la même tâche
                        break
                if core_success == 1: #Si on a finit sans coreSuccess 0, alors ça reste à 1, donc ça a marché. L'assignation de la tâche au core sera acceptée
                    task_to_assign.remove(task_index) #cette liste ne contient pas les tâches successfly assigned
                    assign_to = core #on signale le numéro du core m où la tâche sera enregistrée
                    successfully_assigned = 1 #flag qui dit qu'au moins une seule attempt de assigner une tâche à un core est réussie. pour la boucle qui
                    #appelle cette fonction
                    break #on break le for du core pour ne pas continuer à assigner aux core suivant car place trouvées
            if assign_to == -1: 
                # Si on a réussi à assigner à aucun core alors, on l'ajoute a tna, qui regroupe les tâches assignée a aucun core
                # taskincore[core].remove(task_index)
                task_not_assigned.append(task_index)
        return task_in_core, task_not_assigned, successfully_assigned

    def compute_interference(self, task_index, core_index, task_in_core, task_to_assign):
        #Fonction qui compute le cache interférence, et lance la computation iterative pour trouver le upperbound
        I_run = 0
        I_run_old = 1
        wcet_updated = numpy.copy(self.wcet) #pour faire les modifs on préfère sauvegarder wcet et ne pas le modifier inutilement
        while I_run_old != I_run: #si entre deux tours de boucle on arrive à un résultats similaire à l'ancien, on s'arrête. Iterative 
        #computation expliquée dans le papier    
            I_run_old = I_run #save le run dans le old pour la comparaison
            I_run = 0 #on recommence à 0
            interference_index = self.compute_upper_bound_cache_interference(task_index=task_index, core_index=core_index, execution_window=wcet_updated[task_index], task_in_core=task_in_core, task_to_assign=task_to_assign)
            time.sleep(0.0002)
            if interference_index != None: #si la fonction I run avec l'ILP renvoie un résultat pour l'interference, alors on l'assigne
                I_run = interference_index #on a un nouveau I_run la boucle tournera
            else:
                I_run = 0 #aucune nouvelle interference trouvée, la boucle sera finie car I et I run old 0
            wcet_updated[task_index] = self.wcet[task_index] + I_run #ça marche toujours car si rien à ajouter on ajoute 0

            if wcet_updated[task_index] > self.period[task_index]:
                return self.period[task_index] #Le wcet trouvé fait qu'on pourra pas atteindre la deadline, on renvoie la période pour faire comprendre ça

        return wcet_updated[task_index] #on renvoie juste un seul wcet modifié, celui de la tâche testée dans le core spécifique

    def compute_upper_bound_cache_interference(self, task_index, core_index, execution_window, task_in_core, task_to_assign):
        prob = LpProblem("Upper_Bound_on_Cache_Interference", LpMaximize)
        N_i_k = {}
        max_N_minus_2 = LpVariable.dicts("max_N_minus_2", list(range(len(self.period))), lowBound=0, cat='Integer') #pour remplacer max(0, N-2) contrainte 1.11 
        for task_i in range(len(self.period)):
            N_i_k[task_i] = LpVariable(f"N_{task_i}_{task_index}", lowBound=0, upBound=None, cat='Integer')            
            prob += max_N_minus_2[task_i] >= 0
            prob += max_N_minus_2[task_i] >= N_i_k[task_i] - 2 
            if task_i in task_in_core[core_index] or task_index == task_i:
                #contrainte 1.8
                prob += N_i_k[task_i] == 0
            else:
                #contrainte 1.9
                prob +=  math.floor(max(0, execution_window-self.period[task_i])/ (self.period[task_i])) + (1 if (execution_window % self.period[task_i] - self.period[task_i]) > 0 else 0) <= N_i_k[task_i]
                #contrainte 1.10
                prob += N_i_k[task_i] <= 1 + math.ceil(max(0, execution_window - self.period[task_i] + self.deadline[task_i]) / self.period[task_i])
        
        for core in range(self.number_of_cores):
            if core != core_index:
                #contrainte 1.11
                prob += lpSum([(max_N_minus_2[i]*self.wcet[i]) for i in task_in_core[core] if i != task_index]) \
               + lpSum([(max_N_minus_2[i]*self.wcet[i]) for i in task_to_assign if i != task_index]) <= execution_window    

        #fonction objective        
        prob += lpSum([N_i_k[i] * self.interference[i][task_index] for i in range(len(self.period))])

        gurobi_solver = GUROBI_CMD(msg=0, options=[("OutputFlag", 0)])
        prob.solve(gurobi_solver)
        #prob.solve(GUROBI(msg=0, options=[("OutputFlag", 0)]))
        solution = pulp.value(prob.objective)
        return solution

    def check_one_task(self, task_index, core, wcet_with_interference):
        dbf_list = self.dbf(task_index=task_index, core=core, wcet_with_interference=wcet_with_interference) 
        dbf_sum= self.compute_dbf_sum(dbf_list=dbf_list) 
        blocking_task_index = self.find_max_blocking(task_index=task_index, core=core, wcet_with_interference=wcet_with_interference) 
        if (blocking_task_index == -1):  #trouvé aucun max blocking donc on calcule la condition sans.
            if (self.period[task_index] >= dbf_sum):
                return 1
            else:
                return 0
        else: #trouvé un max blocking time, on calcule la condition 1.6 avec
            if (self.period[task_index] >= dbf_sum + wcet_with_interference[blocking_task_index]):
                return 1
            else:
                return 0

    def dbf(self, task_index, core, wcet_with_interference):
        dbf_list = list()
        for j in core:
            if self.period[task_index] < self.period[j]: #cas où on ne calcule pas le DBF 
                dbf_list.append(0)
            else:
                utilisation_with_interference = float(wcet_with_interference[j] / self.period[j]) 
                dbf_j = wcet_with_interference[j] + (self.period[task_index] - self.period[j]) * utilisation_with_interference  #formule approximation dbf pour tâche k, en temps t=deadline de task_i 
                dbf_list.append(dbf_j)
        return dbf_list

    def compute_dbf_sum(self, dbf_list):
        dbf_sum = 0
        for i in range(0, len(dbf_list)):
            dbf_sum = dbf_sum + dbf_list[i]
        return dbf_sum

    def find_max_blocking(self, task_index, core, wcet_with_interference):
        max_value = 0
        index = -1
        for j in core:
            if self.period[task_index] < self.period[j]: #si la période de la tâche j est plus grande que la tâche dont on calcule le dbf, donc si la priorité est plus petite
                if wcet_with_interference[j] > max_value: #si le wcet de la tâche est le plus grand, ça devient le nouveau max
                    max_value = wcet_with_interference[j]
                    index = j #recherche classique de max
        return index #retourne l'index de la tâche qui pourrait induire un temps bloquant

