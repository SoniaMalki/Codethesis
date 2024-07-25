from pulp import *
import time


class Wmin:
    def __init__(self, taskset, number_of_cores, assignment_options):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.utilization = self.taskset.utilization
        self.interference = self.taskset.interference
        self.single_interference = self.taskset.single_interference
        self.solving_time_limit_MILP = assignment_options.get(
            "solving_time_limit_MILP", None)
        self.assignment_options = assignment_options

    def createLpVariables(self):
        # Variables
        o = {}
        U_M = {}
        maxW_k = {}
        z = {}

        for k in range(self.number_of_cores):
            U_M[k] = LpVariable(f"U_M_{k}", lowBound=0)
            maxW_k[k] = LpVariable(f"maxW_{k}", lowBound=0)
            for i in range(len(self.taskset)):
                o[i, k] = LpVariable(f"o_{i}_{k}", cat='Binary')
                for j in range(len(self.taskset)):
                    if i != j and self.single_interference[i] != 0 and self.single_interference[j] != 0:
                        z[i, j, k] = LpVariable(f"z_{i}_{j}_{k}", cat='Binary')

        maxW = LpVariable("maxW", lowBound=0)

        return o, U_M, maxW_k, maxW, z

    def createLpConstraints(self, prob, o, U_M, maxW_k, maxW, z):
        # Constraints

        # Constraint 19
        for i in range(len(self.taskset)):
            prob += lpSum([o[i, k] for k in range(self.number_of_cores)]) == 1

        # Constraint 20
        for k in range(self.number_of_cores):
            prob += lpSum([self.utilization[i] * o[i, k]
                          for i in range(len(self.taskset))]) == U_M[k]

        # Constraint 21
        for k in range(self.number_of_cores):
            prob += U_M[k] <= 1

        # Constraint 22
        for k in range(self.number_of_cores):
            for i in range(len(self.taskset)):
                if self.single_interference[i] != 0:
                    for j in range(len(self.taskset)):
                        if i != j and self.single_interference[j] != 0:
                            # Variable pour o[i, k] * (1 - o[j, k]) (s'assurer que i et j comptent l'interference que si coeur diff (que i dans coeur k))
                            prob += z[i, j, k] <= o[i, k]
                            prob += z[i, j, k] <= (1 - o[j, k])
                            prob += z[i, j, k] >= o[i, k] + (1 - o[j, k]) - 1

            prob += lpSum([self.single_interference[j] * z[i, j, k]
                           for i in range(len(self.taskset)) if self.single_interference[i] != 0
                           for j in range(len(self.taskset)) if i != j and self.single_interference[j] != 0
                           ]) == maxW_k[k]

        # Objective function
        prob += maxW == lpSum([maxW_k[k] for k in range(self.number_of_cores)])
        prob += maxW

    def assign(self):
        prob = LpProblem("Wmin_Assignment", LpMinimize)

        o, U_M, maxW_k, maxW, z = self.createLpVariables()
        self.createLpConstraints(prob, o, U_M, maxW_k, maxW, z)

        # Solving the MILP problem
        options = [("OutputFlag", 0)]
        if self.solving_time_limit_MILP is not None:
            options.append(("TimeLimit", self.solving_time_limit_MILP))

        prob.solve(GUROBI_CMD(msg=0, options=options))

        task_in_core = [[] for _ in range(self.number_of_cores)]
        # Checking if a solution is found
        if prob.status == 1:
            for i in range(len(self.taskset)):
                for k in range(self.number_of_cores):
                    if o[i, k].varValue == 1:
                        task_in_core[k].append(i)
            return task_in_core, 1
        elif prob.status == LpStatusNotSolved:
            print("Time limit was hit during optimization.")
            return task_in_core, 0
        else:
            print("Wmin failed to find a solution.")
            return task_in_core, 0
