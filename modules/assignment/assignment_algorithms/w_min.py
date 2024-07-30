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
        self.solver_name = self.assignment_options.get("solver_name", "cbc")
        if self.solver_name == "gurobi":
            self.solver = GUROBI_CMD(msg=0, options=[
                ("OutputFlag", 0)
            ])
        elif self.solver_name == "cbc":
            self.solver = PULP_CBC_CMD(msg=0)
        else:
            raise ValueError(
                f"Solveur non supporté: {self.solver_name}. Choisissez 'gurobi' ou 'cbc'.")

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

    def createLpConstraints(self, o, U_M, maxW_k, maxW, z):
        constraint_19 = []
        constraint_20 = []
        constraint_21 = []
        constraint_22 = []

        # Constraint 19
        for i in range(len(self.taskset)):
            constraint_19.append(lpSum(
                [o[i, k] for k in range(self.number_of_cores)]) == 1)

        # Constraint 22
        for k in range(self.number_of_cores):
            constraint_20.append(lpSum([self.utilization[i] * o[i, k]
                                        for i in range(len(self.taskset))]) == U_M[k])
            constraint_21.append(U_M[k] <= 1)
            for i in range(len(self.taskset)):
                if self.single_interference[i] != 0:
                    for j in range(len(self.taskset)):
                        if i != j and self.single_interference[j] != 0:
                            # Variable pour o[i, k] * (1 - o[j, k]) (s'assurer que i et j comptent l'interference que si coeur diff (que i dans coeur k))
                            constraint_22.append(z[i, j, k] <= o[i, k])
                            constraint_22.append(z[i, j, k] <= (1 - o[j, k]))
                            constraint_22.append(
                                z[i, j, k] >= o[i, k] + (1 - o[j, k]) - 1)

            constraint_22.append(lpSum([self.single_interference[j] * z[i, j, k]
                                        for i in range(len(self.taskset)) if self.single_interference[i] != 0
                                        for j in range(len(self.taskset)) if i != j and self.single_interference[j] != 0
                                        ]) == maxW_k[k])

        return constraint_19, constraint_20, constraint_21, constraint_22

    def assign(self):
        prob = LpProblem("Wmin_Assignment", LpMinimize)

        o, U_M, maxW_k, maxW, z = self.createLpVariables()
        constraint_19, constraint_20, constraint_21, constraint_22 = self.createLpConstraints(
            o, U_M, maxW_k, maxW, z)

        for constraint in constraint_19:
            prob += constraint
        for constraint in constraint_20:
            prob += constraint
        for constraint in constraint_21:
            prob += constraint
        for constraint in constraint_22:
            prob += constraint

        # Objective function
        prob += maxW == lpSum(
            [maxW_k[k] for k in range(self.number_of_cores)])
        prob += maxW

        # Solving the MILP problem
        if self.solving_time_limit_MILP is not None:
            if self.solver_name == "gurobi":
                self.solver.options.append(
                    ("TimeLimit", self.solving_time_limit_MILP))
            elif self.solver_name == "cbc":
                self.solver.options.extend(
                    ["sec", str(self.solving_time_limit_MILP)])

        prob.solve(self.solver)

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
