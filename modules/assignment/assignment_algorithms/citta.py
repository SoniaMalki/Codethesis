import numpy
import math
from pulp import *


class Citta:
    def __init__(self, taskset, number_of_cores, sorting_criterion, assignment_options):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.period = self.taskset.period
        self.deadline = self.taskset.deadline
        self.wcet = self.taskset.wcet
        self.interference = self.taskset.interference
        self.utilization = self.taskset.utilization
        self.sorting_criterion = sorting_criterion
        self.assignment_options = assignment_options

        self.solving_time_limit_MILP = self.assignment_options.get(
            "solving_time_limit_MILP", None)

        self.solver_name = self.assignment_options.get("solver_name", "gurobi")

        print(f"Citta utilisant le solveur : {self.solver_name}")

        if self.solver_name == "gurobi":
            self.solver = GUROBI_CMD(msg=0, options=[("OutputFlag", 0)])
        elif self.solver_name == "glpk":
            self.solver = GLPK_CMD(msg=0)
        else:
            raise ValueError(
                f"Solveur non supporté: {self.solver_name}. Choisissez 'gurobi' ou 'glpk'.")

    def sort_task(self):
        # Trie les tâches selon certains critères
        taskset = list(range(len(self.taskset)))

        if self.sorting_criterion == "wcet_ascending":
            taskset = sorted(taskset, key=lambda k: self.wcet[k])
        elif self.sorting_criterion == "wcet_descending":
            taskset = sorted(taskset, key=lambda k: self.wcet[k], reverse=True)
        elif self.sorting_criterion == "period_ascending":
            taskset = sorted(taskset, key=lambda k: self.period[k])
        elif self.sorting_criterion == "period_descending":
            taskset = sorted(
                taskset, key=lambda k: self.period[k], reverse=True)
        elif self.sorting_criterion == "utilization_ascending":
            taskset = sorted(taskset, key=lambda k: self.utilization[k])
        elif self.sorting_criterion == "utilization_descending":
            taskset = sorted(
                taskset, key=lambda k: self.utilization[k], reverse=True)
        elif self.sorting_criterion == "execution_slack_ascending":
            taskset = sorted(
                taskset, key=lambda k: self.period[k] - self.wcet[k])
        elif self.sorting_criterion == "execution_slack_descending":
            taskset = sorted(
                taskset, key=lambda k: self.period[k] - self.wcet[k], reverse=True)
        elif self.sorting_criterion == "random_order":
            numpy.random.shuffle(taskset)
        else:
            print(
                f"Invalid sorting criterion: {self.sorting_criterion}. Returning tasks in random order.")
            numpy.random.shuffle(taskset)
        return taskset

    def assign(self):
        taskset = self.sort_task()
        taskset_not_assigned = taskset[:]
        successfully_assigned = 1
        task_in_core = [[] for _ in range(self.number_of_cores)]
        while taskset_not_assigned and successfully_assigned == 1:
            task_in_core, taskset_not_assigned, successfully_assigned = self.task_partition(
                taskset=taskset_not_assigned, task_in_core=task_in_core)

        if not taskset_not_assigned:
            return task_in_core, 1
        else:
            return task_in_core, 0

    def task_partition(self, taskset, task_in_core):
        successfully_assigned = 0
        task_not_assigned = []
        task_to_assign = taskset[:]
        for task_index in taskset:
            assign_to = -1  # core par défaut
            for core in range(self.number_of_cores):
                task_in_core[core].append(task_index)
                wcet_with_interference = numpy.copy(self.wcet)
                core_success = 1
                for task in task_in_core[core]:
                    interference, success = self.compute_interference(
                        task_index=task, core_index=core, task_in_core=task_in_core, task_to_assign=task_to_assign)
                    if not success:
                        return task_in_core, task_to_assign, 0  # Time limit hit, stop immediately
                    wcet_with_interference[task] = interference
                for task in task_in_core[core]:
                    if self.check_one_task(task_index=task, core=task_in_core[core], wcet_with_interference=wcet_with_interference) == 0:
                        task_in_core[core].remove(task_index)
                        core_success = 0
                        break
                if core_success == 1:
                    task_to_assign.remove(task_index)
                    assign_to = core
                    successfully_assigned = 1
                    break
            if assign_to == -1:
                task_not_assigned.append(task_index)
        return task_in_core, task_not_assigned, successfully_assigned

    def compute_interference(self, task_index, core_index, task_in_core, task_to_assign):
        I_run = 0
        I_run_old = 1
        # copie wcet pour modif temporaire
        wcet_updated = numpy.copy(self.wcet)
        # si entre deux tours de boucle on arrive à un résultats similaire à l'ancien, on s'arrête.
        while I_run_old != I_run and wcet_updated[task_index] <= self.period[task_index]:
            I_run_old = I_run
            I_run, success = self.compute_upper_bound_cache_interference(
                task_index=task_index, core_index=core_index, execution_window=wcet_updated[task_index], task_in_core=task_in_core, task_to_assign=task_to_assign)
            # ça marche toujours car si rien à ajouter on ajoute 0

            if not success:
                return self.period[task_index], False  # Time limit hit
            wcet_updated[task_index] = self.wcet[task_index] + I_run

        if wcet_updated[task_index] > self.period[task_index]:
            # Le wcet trouvé fait qu'on pourra pas atteindre la deadline, on renvoie la période pour faire comprendre ça
            res = self.period[task_index]
        else:
            # on renvoie juste un seul wcet modifié, celui de la tâche testée dans le core spécifique
            res = wcet_updated[task_index]
        return res, True

    def createLpVariablesForCacheInterference(self, task_index, execution_window, core_index, task_in_core, task_to_assign):
        N_i_k = {}
        max_N_minus_2 = LpVariable.dicts("max_N_minus_2", list(range(len(
            self.period))), lowBound=0, cat='Integer')  # pour remplacer max(0, N-2) contrainte 1.11
        for task_i in range(len(self.period)):
            N_i_k[task_i] = LpVariable(
                f"N_{task_i}_{task_index}", lowBound=0, upBound=None, cat='Integer')

        return N_i_k, max_N_minus_2

    def createLpConstraintsForCacheInterference(self, prob, task_index, execution_window, core_index, task_in_core, task_to_assign, N_i_k, max_N_minus_2):
        # Constraints
        for task_i in range(len(self.period)):
            prob += max_N_minus_2[task_i] >= 0
            prob += max_N_minus_2[task_i] >= N_i_k[task_i] - 2
            if task_i in task_in_core[core_index] or task_index == task_i:
                # contrainte 1.8
                prob += N_i_k[task_i] == 0
            else:
                # contrainte 1.9
                prob += math.floor(max(0, execution_window-self.period[task_i]) / (self.period[task_i])) + (
                    1 if ((execution_window % self.period[task_i]) - self.deadline[task_i]) > 0 else 0) <= N_i_k[task_i]
                # contrainte 1.10
                prob += N_i_k[task_i] <= 1 + math.ceil(max(
                    0, execution_window - self.period[task_i] + self.deadline[task_i]) / self.period[task_i])

        for core in range(self.number_of_cores):
            if core != core_index:
                # contrainte 1.11
                prob += lpSum([(max_N_minus_2[i]*self.wcet[i]) for i in task_in_core[core] if i != task_index]) \
                    + lpSum([(max_N_minus_2[i]*self.wcet[i])
                            for i in task_to_assign if i != task_index]) <= execution_window

        # fonction objective
        prob += lpSum([N_i_k[i] * self.interference[i][task_index]
                      for i in range(len(self.period))])

    def compute_upper_bound_cache_interference(self, task_index, core_index, execution_window, task_in_core, task_to_assign):
        prob = LpProblem("Upper_Bound_on_Cache_Interference", LpMaximize)

        N_i_k, max_N_minus_2 = self.createLpVariablesForCacheInterference(
            task_index, execution_window, core_index, task_in_core, task_to_assign)
        self.createLpConstraintsForCacheInterference(
            prob, task_index, execution_window, core_index, task_in_core, task_to_assign, N_i_k, max_N_minus_2)

        if self.solving_time_limit_MILP is not None:
            if self.solver_name == "gurobi":
                self.solver.options.append(
                    ("TimeLimit", self.solving_time_limit_MILP))
        prob.solve(self.solver)
        solution = pulp.value(prob.objective)

        # Check if the time limit was hit

        if prob.status == LpStatusNotSolved:
            print("Time limit was hit during optimization.")
            return solution if solution is not None else 0, False
        else:
            return solution if solution is not None else 0, True

    def check_one_task(self, task_index, core, wcet_with_interference):
        dbf_list = self.dbf(task_index=task_index, core=core,
                            wcet_with_interference=wcet_with_interference)
        dbf_sum = self.compute_dbf_sum(dbf_list=dbf_list)
        blocking_task_index = self.find_max_blocking(
            task_index=task_index, core=core, wcet_with_interference=wcet_with_interference)
        # trouvé aucun max blocking donc on calcule la condition sans.
        if (blocking_task_index == -1):
            if (self.period[task_index] >= dbf_sum):
                return 1
            else:
                return 0
        else:  # trouvé un max blocking time, on calcule la condition 1.6 avec
            if (self.period[task_index] >= dbf_sum + wcet_with_interference[blocking_task_index]):
                return 1
            else:
                return 0

    def dbf(self, task_index, core, wcet_with_interference):
        dbf_list = list()
        for j in core:
            if self.period[task_index] < self.period[j]:  # cas où on ne calcule pas le DBF
                dbf_list.append(0)
            else:
                utilisation_with_interference = float(
                    wcet_with_interference[j] / self.period[j])
                # formule approximation dbf pour tâche k, en temps t=deadline de task_i
                dbf_j = wcet_with_interference[j] + (
                    self.period[task_index] - self.period[j]) * utilisation_with_interference
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
            if self.period[task_index] < self.period[j]:
                if wcet_with_interference[j] > max_value:
                    max_value = wcet_with_interference[j]
                    index = j
        return index
