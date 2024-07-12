from pulp import *


class Wmin:
    def __init__(self, taskset, number_of_cores):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.utilization = self.taskset.utilization
        self.interference = self.taskset.interference

    def assign(self):
        prob = LpProblem("Wmin_Assignment", LpMinimize)

        # Variables
        o = {}
        for i in range(len(self.taskset)):
            for k in range(self.number_of_cores):
                o[i, k] = LpVariable(f"o_{i}_{k}", cat='Binary')

        U_M = {}
        for k in range(self.number_of_cores):
            U_M[k] = LpVariable(f"U_M_{k}", lowBound=0)

        maxW_k = {}
        for k in range(self.number_of_cores):
            maxW_k[k] = LpVariable(f"maxW_{k}", lowBound=0)

        maxW = LpVariable("maxW", lowBound=0)

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
            prob += lpSum([self.interference[j] * o[i, k] * (1 - o[j, k])
                           for i in range(len(self.taskset)) if self.interference[i] != 0
                           for j in range(len(self.taskset)) if i != j
                           ]) == maxW_k[k]

        # Objective function
        prob += lpSum([maxW_k[k] for k in range(self.number_of_cores)]) == maxW
        prob += maxW

        # Solving the MILP problem
        prob.solve(GUROBI_CMD(msg=0, options=[("OutputFlag", 0)]))
        print(prob)

        task_in_core = [[] for _ in range(self.number_of_cores)]
        # Checking if a solution is found
        if prob.status == 1:
            for i in range(len(self.taskset)):
                for k in range(self.number_of_cores):
                    if o[i, k].varValue == 1:
                        task_in_core[k].append(i)
            return task_in_core, 1
        else:
            print("Wmin failed to find a solution.")
            return task_in_core, 0
