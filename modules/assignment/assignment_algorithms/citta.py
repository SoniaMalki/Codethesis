import numpy
import math
from pulp import *
from pulp.apis.core import PulpSolverError


class Citta:
    def __init__(self, taskset, number_of_cores, sorting_criterion, assignment_options):
        print("----- Initializing CITTA -----")
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

        # Get thread count from options or default
        self.threads = self.assignment_options.get("threads", 1)
        if self.threads == None:
            self.threads = 1
        if 'threads' in self.assignment_options and self.assignment_options.get("threads", 1) != None:
            print(
                f"Using thread count from assignment_options: {self.threads}")
        else:
            print(f"Using default thread count: {self.threads}")

        print(
            f"Citta utilisant le solveur : {self.solver_name} avec thread {self.threads}")

        if self.solver_name == "gurobi":
            self.solver = GUROBI_CMD(msg=1, options=[("OutputFlag", 1)])
        elif self.solver_name == "glpk":
            self.solver = GLPK_CMD(msg=0)
        else:
            raise ValueError(
                f"Solveur non supporté: {self.solver_name}. Choisissez 'gurobi' ou 'glpk'.")

    def sort_task(self):
        # Trie les tâches selon certains critères
        print("----- Sorting tasks using criterion:",
              self.sorting_criterion, "-----")
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
        print("Tasks sorted:", taskset)
        return taskset

    def assign(self):
        print("----- Starting CITTA Assignment -----")
        taskset = self.sort_task()
        taskset_not_assigned = taskset[:]
        successfully_assigned = 1
        task_in_core = [[] for _ in range(self.number_of_cores)]
        while taskset_not_assigned and successfully_assigned == 1:
            print("----- Entering task_partition Loop -----")
            task_in_core, taskset_not_assigned, successfully_assigned = self.task_partition(
                taskset=taskset_not_assigned, task_in_core=task_in_core)

        if not taskset_not_assigned:
            print("----- CITTA Assignment Completed (Success) -----")
            return task_in_core, 1
        else:
            print("----- CITTA Assignment Completed (Failed) -----")
            return task_in_core, 0

    def task_partition(self, taskset, task_in_core):
        print("----- Entering task_partition -----")
        successfully_assigned = 0
        task_not_assigned = []
        task_to_assign = taskset[:]
        print(f"Tasks to assign: {task_to_assign}")
        for task_index in taskset:
            print(f"Trying to assign task: {task_index}")
            assign_to = -1  # core par défaut
            for core in range(self.number_of_cores):
                print(f"   Trying core {core} for task {task_index}")
                task_in_core[core].append(task_index)
                wcet_with_interference = numpy.copy(self.wcet)
                core_success = 1
                for task in task_in_core[core]:
                    print(
                        f"      Computing interference for task {task} on core {core}")
                    interference, success = self.compute_interference(
                        task_index=task, core_index=core, task_in_core=task_in_core, task_to_assign=task_to_assign)
                    if not success:
                        return task_in_core, task_to_assign, 0  # Time limit hit, stop immediately
                    wcet_with_interference[task] = interference
                for task in task_in_core[core]:
                    print(
                        f"      Checking schedulability for task {task} on core {core}")
                    if self.check_one_task(task_index=task, core=task_in_core[core], wcet_with_interference=wcet_with_interference) == 0:
                        print(
                            f"         Task {task_index} not schedulable on core {core}. Removing")
                        task_in_core[core].remove(task_index)
                        core_success = 0
                        break
                if core_success == 1:
                    print(
                        f"         Task {task_index} successfully assigned to core {core}")
                    task_to_assign.remove(task_index)
                    assign_to = core
                    successfully_assigned = 1
                    break
            if assign_to == -1:
                print(
                    f"      Task {task_index} could not be assigned to any core. Adding to task_not_assigned")
                task_not_assigned.append(task_index)
        print("----- Exiting task_partition -----")
        return task_in_core, task_not_assigned, successfully_assigned

    def compute_interference(self, task_index, core_index, task_in_core, task_to_assign):
        print("----- Computing interference for task:",
              task_index, "on core:", core_index, "-----")
        I_run = 0
        I_run_old = -1
        # copie wcet pour modif temporaire
        wcet_updated = numpy.copy(self.wcet)
        # si entre deux tours de boucle on arrive à un résultats similaire à l'ancien, on s'arrête.
        while I_run_old < I_run and wcet_updated[task_index] <= self.period[task_index]:
            I_run_old = I_run
            print(
                f"         Computing upper bound on cache interference for task {task_index} with execution window: {wcet_updated[task_index]}")
            I_run, success = self.compute_upper_bound_cache_interference(
                task_index=task_index, core_index=core_index, execution_window=wcet_updated[task_index], task_in_core=task_in_core, task_to_assign=task_to_assign)
            # ça marche toujours car si rien à ajouter on ajoute 0

            if not success:
                print(
                    "Interference computation failed (Time Limit Hit). Returning period.")
                return self.period[task_index], False  # Time limit hit
            wcet_updated[task_index] = self.wcet[task_index] + I_run
            print(
                f"         Updated wcet for task {task_index}: {wcet_updated[task_index]}")

        if wcet_updated[task_index] > self.period[task_index]:
            # Le wcet trouvé fait qu'on pourra pas atteindre la deadline, on renvoie la période pour faire comprendre ça
            print("         WCET exceeds period. Returning period as interference.")
            res = self.period[task_index]
        else:
            # on renvoie juste un seul wcet modifié, celui de la tâche testée dans le core spécifique
            res = wcet_updated[task_index]
        print("Interference computed:", res)
        return res, True

    def createLpVariablesForCacheInterference(self, task_index, execution_window, core_index, task_in_core, task_to_assign):
        print("----- Creating LP variables for cache interference -----")
        N_i_k = {}
        max_N_minus_2 = LpVariable.dicts("max_N_minus_2", list(range(len(
            self.period))), lowBound=0, cat='Integer')  # pour remplacer max(0, N-2) contrainte 1.11
        for task_i in range(len(self.period)):
            N_i_k[task_i] = LpVariable(
                f"N_{task_i}_{task_index}", lowBound=0, upBound=None, cat='Integer')
        print("LP Variables for cache interference created.")
        return N_i_k, max_N_minus_2

    def createLpConstraintsForCacheInterference(self, prob, task_index, execution_window, core_index, task_in_core, task_to_assign, N_i_k, max_N_minus_2):
        # Constraints
        print("----- Creating LP constraints for cache interference -----")
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
        print("LP Constraints for cache interference created.")

    def compute_upper_bound_cache_interference(self, task_index, core_index, execution_window, task_in_core, task_to_assign):
        print("----- Computing upper bound on cache interference for task:",
              task_index, "-----")
        prob = LpProblem("Upper_Bound_on_Cache_Interference", LpMaximize)

        N_i_k, max_N_minus_2 = self.createLpVariablesForCacheInterference(
            task_index, execution_window, core_index, task_in_core, task_to_assign)
        self.createLpConstraintsForCacheInterference(
            prob, task_index, execution_window, core_index, task_in_core, task_to_assign, N_i_k, max_N_minus_2)

        if self.solving_time_limit_MILP is not None and type(self.solving_time_limit_MILP) == int:
            if self.solver_name == "gurobi":
                self.solver.options.append(
                    ("TimeLimit", self.solving_time_limit_MILP))

        if self.solver_name == "gurobi":
            # Set thread count for Gurobi
            self.solver.options.append(("Threads", self.threads))

        max_retries = 100
        retries = 0
        success = False
        while retries < max_retries and not success:
            try:
                prob.solve(self.solver)
                solution = pulp.value(prob.objective)

                # Check if the time limit was hit

                if prob.status == LpStatusNotSolved:
                    print("Time limit was hit during optimization.")
                    return solution if solution is not None else 0, False
                else:
                    print("Upper bound computed:", solution)
                    return solution if solution is not None else 0, True
            except PulpSolverError:
                retries += 1
                print(f"Gurobi error, retrying {retries}/{max_retries}")
                success = False

        if retries >= max_retries:
            # Raise the exception if the limit is reached
            raise PulpSolverError(
                "Gurobi failed to solve after multiple attempts.")

    def check_one_task(self, task_index, core, wcet_with_interference):
        print("----- Checking schedulability of task:",
              task_index, "on core with tasks:", core, "-----")
        dbf_list = self.dbf(task_index=task_index, core=core,
                            wcet_with_interference=wcet_with_interference)
        dbf_sum = self.compute_dbf_sum(dbf_list=dbf_list)
        blocking_task_index = self.find_max_blocking(
            task_index=task_index, core=core, wcet_with_interference=wcet_with_interference)
        # trouvé aucun max blocking donc on calcule la condition sans.
        if (blocking_task_index == -1):
            if (self.period[task_index] >= dbf_sum):
                print(f"      Task {task_index} schedulable")
                result = 1
            else:
                print(f"      Task {task_index} not schedulable")
                result = 0
        else:  # trouvé un max blocking time, on calcule la condition 1.6 avec
            if (self.period[task_index] >= dbf_sum + wcet_with_interference[blocking_task_index]):
                print(f"      Task {task_index} schedulable")
                result = 1
            else:
                print(f"      Task {task_index} not schedulable")
                result = 0
        print("Schedulability check result:", result)
        return result

    def dbf(self, task_index, core, wcet_with_interference):
        print(
            f"      Computing DBF for task {task_index} on core with tasks: {core}")
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
        print(f"      DBF values for task {task_index}: {dbf_list}")
        return dbf_list

    def compute_dbf_sum(self, dbf_list):
        print("      Computing DBF sum")
        dbf_sum = 0
        for i in range(0, len(dbf_list)):
            dbf_sum = dbf_sum + dbf_list[i]
        print("      DBF sum:", dbf_sum)
        return dbf_sum

    def find_max_blocking(self, task_index, core, wcet_with_interference):
        print(f"      Finding max blocking task for task {task_index}")
        max_value = 0
        index = -1
        for j in core:
            if self.period[task_index] < self.period[j]:
                if wcet_with_interference[j] > max_value:
                    max_value = wcet_with_interference[j]
                    index = j
        print(
            f"      Max blocking task index: {index}, max blocking value: {max_value}")
        return index
