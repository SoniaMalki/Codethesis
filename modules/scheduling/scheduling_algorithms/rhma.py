import math
from pathlib import Path
from itertools import product
from pulp import *
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from modules.scheduling.scheduling import Scheduling
from modules.scheduling.scheduling_algorithms.combined_scheduler import CombinedScheduler
from modules.utils.busy_period import BusyPeriod


class Rhma:
    def __init__(self, taskset, assignment, number_of_cores, scheduling_options, start_time=0, end_time=None):
        # print("----- Initializing RHMA -----")
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.assignment = assignment
        self.number_of_cores = number_of_cores
        self.scheduling_options = scheduling_options
        self.test_mode = self.scheduling_options.get("test_mode", False)
        if self.test_mode:
            self.seed = self.scheduling_options.get("seed", 42)

        self.solving_time_limit_MILP = self.scheduling_options.get(
            "solving_time_limit_MILP", None)

        if end_time is None:
            end_time = self.hyperperiod

        self.start_time = start_time
        self.end_time = end_time
        # Parameters generated after assignment
        self.o_i_j = self.generate_o_i_j()
        self.maxI = self.generate_max_I()
        self.combined_scheduler = CombinedScheduler(taskset=self.taskset, assignment=self.assignment,
                                                    number_of_cores=self.number_of_cores, scheduling_options=self.scheduling_options,
                                                    start_time=self.start_time,
                                                    end_time=self.end_time)
        self.busy_periods = self.combined_scheduler.schedule()
        self.actual_utilization = self.combined_scheduler.actual_utilization

        # Parameters generated after busy period generation
        self.S_i_h = self.generate_S_i_h()
        self.R_i_a_h = self.generate_R_i_a_h(self.S_i_h)
        self.T_h = self.generate_T_h()
        self.d_i_a = self.taskset.absolute_deadline

        # Save parameters to file to analyse
        # output_path = f"{Path(__file__).parent.parent.parent.parent}/other_files/output_parameters.txt"
        # self.save_parameters_to_file(file_path = output_path)

        self.solver_name = self.scheduling_options.get(
            "solver_name", "gurobi")

        # Get thread count from options or default
        self.threads = self.scheduling_options.get("threads", 8)
        if self.threads is None:
            self.threads = 10
        if 'threads' in self.scheduling_options and self.scheduling_options.get("threads", 1) is not None:
            print(
                f"Using thread count from scheduling_options: {self.threads}")
        else:
            print(f"Using default thread count: {self.threads}")

        print(
            f"Rhma utilisant le solveur : {self.solver_name} avec thread {self.threads}")

        if self.solver_name == "gurobi":
            self.solver = GUROBI_CMD(msg=0, options=[
                ("OutputFlag", 0),
                ("Seed", self.seed)
            ] if self.test_mode else [("OutputFlag", 0), ("Threads", self.threads)])
        elif self.solver_name == "glpk":
            self.solver = GLPK_CMD(msg=0)
        else:
            raise ValueError(
                f"Solveur non supporté: {self.solver_name}. Choisissez 'gurobi' ou 'glpk'.")

    def output_parameters_to_str(self):
        output_res = "---------------------\n Parameters \n---------------------\n"
        output_res += f"N: {self.taskset.N} \n"
        output_res += f"C: {self.taskset.wcet} \n"
        output_res += f"D: {self.taskset.deadline} \n"
        output_res += f"T: {self.taskset.period} \n"
        output_res += f"I: {self.taskset.single_interference} \n"
        output_res += f"Hyperperiod: {self.taskset.hyperperiod} \n"
        output_res += f"Activation: {self.taskset.activation} \n"
        output_res += f"Absolute deadline: {self.taskset.absolute_deadline} \n"
        output_res += f"maxI: {self.maxI} \n"
        output_res += f"o_i_j: {self.o_i_j} \n"
        output_res += f"Number of busy periods: {len(self.busy_periods)} \n"
        output_res += f"S_i_h: {self.S_i_h} \n"
        output_res += f"R_i_a_h: {self.R_i_a_h} \n"
        output_res += f"T_h: {self.T_h} \n"

        return output_res

    def save_parameters_to_file(self, file_path):
        output_res = self.output_parameters_to_str()
        with open(file_path, 'w') as file:
            file.write(output_res)

    def __str__(self):
        return self.__class__.__name__

    def generate_max_I(self):
        print("----- Generating maxI -----")
        maxI = 0
        for i, j in product(range(len(self.taskset)), repeat=2):
            if i != j and not np.array_equal(self.o_i_j[i], self.o_i_j[j]) and self.taskset.single_interference[i] != 0 and self.taskset.single_interference[j] != 0:
                v_j_to_i = self.calculate_activation_pattern(j=j, i=i)
                for a_index, a in enumerate(self.taskset.activation[i]):
                    maxI += v_j_to_i[a_index] * \
                        self.taskset[j].single_interference
        return maxI

    def calculate_activation_pattern(self, j, i):
        v_j_to_i = np.ones(len(self.taskset.activation[i]), dtype=np.int32)
        for a_idx, a in enumerate(self.taskset.activation[i]):
            activation_start = (a-1) * self.taskset.period[i] + 1
            activation_end = a * self.taskset.period[i]
            for t in range(activation_start, activation_end):
                if t % self.taskset.period[j] == 0:
                    v_j_to_i[a_idx] += 1
        return v_j_to_i

    def generate_o_i_j(self):
        print("----- Generating o_i_j -----")
        tasks_per_core = {core: set() for core in range(self.number_of_cores)}
        for core, tasks in self.assignment.items():
            tasks_per_core[core].update(tasks)

        o_i_j = np.zeros(
            (len(self.taskset), self.number_of_cores), dtype=np.int32)
        for task_index in range(len(self.taskset)):
            for core in range(self.number_of_cores):
                if task_index in tasks_per_core[core]:
                    o_i_j[task_index, core] = 1

        print(f"o_i_j generated: {o_i_j}")
        return o_i_j

    def generate_S_i_h(self):
        print("----- Generating S_i_h -----")
        S_i_h = np.empty((len(self.taskset), len(
            self.busy_periods)), dtype=object)
        for i in range(len(self.taskset)):
            for h in range(len(self.busy_periods)):
                S_i_h[i, h] = []
                task_period = self.taskset.period[i]
                for a in self.taskset.activation[i]:
                    activation_start = ((a - 1) * task_period) + 1
                    busy_period = self.busy_periods[h]
                    if busy_period.start_time <= activation_start < busy_period.end_time:
                        S_i_h[i, h].append(a)
        return S_i_h

    def generate_R_i_a_h(self, S_i_h):
        print("----- Generating R_i_a_h -----")
        R_i_a_h = np.empty(
            (len(self.taskset), len(self.busy_periods)), dtype=object)
        for i in range(len(self.taskset)):
            for h in range(len(self.busy_periods)):
                R_i_a_h[i, h] = {}
                task_period = self.taskset.period[i]
                for a in S_i_h[i, h]:
                    activation_start = ((a - 1) * task_period) + 1
                    activation_end = a * task_period + 1
                    busy_period = self.busy_periods[h]

                    intersection_start = max(
                        activation_start, busy_period.start_time)
                    intersection_end = min(
                        activation_end, busy_period.end_time)

                    R_i_a_h[i, h][a] = np.arange(
                        intersection_start, intersection_end)
        return R_i_a_h

    def generate_T_h(self):
        print("----- Generating T_h -----")
        T_h = np.empty(len(self.busy_periods), dtype=object)
        for h, busy_period in enumerate(self.busy_periods):
            T_h[h] = np.arange(busy_period.start_time, busy_period.end_time)
        return T_h

    def createLpVariables(self, h):
        # Variables

        print(f"----- Creating LP variables for busy period {h} -----")

        w = LpVariable.dicts(
            "w",
            [(i, a) for i in range(len(self.taskset))
             for a in self.S_i_h[i, h]],
            lowBound=0,
            cat='Integer'
        )

        x = LpVariable.dicts(
            "x",
            [(i, a, j, t)
             for i in range(len(self.taskset))
             for a in self.S_i_h[i, h]
             for j, t in product(
                range(self.number_of_cores),
                self.T_h[h]
            )
            ],
            cat='Binary'
        )

        m = LpVariable.dicts(
            "m",
            [(i, a, k, b)
             for i, k in product(range(len(self.taskset)), repeat=2)
             for a in self.S_i_h[i, h]
             for b in self.S_i_h[k, h]
             ],
            cat='Binary'
        )

        print("LP Variables created.")
        return x, m, w

    def extract_s_i_h_for_h(self, h):
        s_i_h_for_h = {i: self.S_i_h[i, h] for i in range(
            len(self.taskset)) if h < len(self.S_i_h[i])}
        return s_i_h_for_h

    def extract_r_i_a_h_for_h(self, h, s_i_h_for_h):
        r_i_a_h_for_h = {}
        for i, activations in s_i_h_for_h.items():
            r_i_a_h_for_h[i] = {}
            for a in activations:
                activation_start = ((a-1) * self.taskset.period[i]) + 1
                activation_end = a * self.taskset.period[i] + 1
                busy_period = self.busy_periods[h]

                intersection_start = max(
                    activation_start, busy_period.start_time)
                intersection_end = min(activation_end, busy_period.end_time)

                r_i_a_h_for_h[i][a] = np.arange(
                    intersection_start, intersection_end)
        return r_i_a_h_for_h

    def create_constraint_16(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 16 for busy period {h} -----")
        constraint_16 = []
        for i, activations in s_i_h_for_h.items():
            for a in activations:
                for j in range(self.number_of_cores):
                    for t in self.T_h[h]:
                        if self.o_i_j[i, j] == 0:
                            constraint_16.append(x[i, a, j, t] == 0)
        print(f"----- Constraint 16 created for busy period {h} -----")
        return constraint_16

    def create_constraint_17(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 17 for busy period {h} -----")
        constraint_17 = []
        for i, activations in s_i_h_for_h.items():
            for k in range(i + 1, len(s_i_h_for_h)):
                activations_i = s_i_h_for_h[i]
                activations_k = s_i_h_for_h[k]
                for a, b in product(activations_i, activations_k):
                    if not np.intersect1d(r_i_a_h_for_h[i][a], r_i_a_h_for_h[k][b]).size:
                        constraint_17.append(m[i, a, k, b] == 0)
        print(f"----- Constraint 17 created for busy period {h} -----")
        return constraint_17

    def create_constraint_18(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 18 for busy period {h} -----")
        constraint_18 = []
        for i, activations in s_i_h_for_h.items():
            for j in range(self.number_of_cores):
                if activations:
                    left_side = lpSum(x[i, a, j, t]
                                      for a in activations for t in r_i_a_h_for_h[i][a])
                    right_side = len(activations) * \
                        self.taskset.wcet[i] * self.o_i_j[i, j]

                    right_side += lpSum(m[i, a, k, b] * self.taskset.single_interference[k] * self.o_i_j[i, j]
                                        for k, b_activations in s_i_h_for_h.items() if k != i and self.o_i_j[i, j] != self.o_i_j[k, j] and self.taskset.single_interference[k] > 0 and self.taskset.single_interference[i] > 0
                                        for a in activations for b in b_activations)

                    constraint_18.append(left_side == right_side)
        print(f"----- Constraint 18 created for busy period {h} -----")
        return constraint_18

    def create_constraint_19(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 19 for busy period {h} -----")
        constraint_19 = []
        for i, activations in s_i_h_for_h.items():
            for a in activations:
                for j in range(self.number_of_cores):
                    if activations:
                        left_side = lpSum(x[i, a, j, t]
                                          for t in r_i_a_h_for_h[i][a])
                        right_side = self.taskset.wcet[i] * self.o_i_j[i, j]

                        right_side += lpSum(m[i, a, k, b] * self.taskset.single_interference[k] * self.o_i_j[i, j]
                                            for k, b_activations in s_i_h_for_h.items() if k != i and self.o_i_j[i, j] != self.o_i_j[k, j] and self.taskset.single_interference[k] > 0 and self.taskset.single_interference[i] > 0
                                            for b in b_activations)

                        constraint_19.append(left_side == right_side)
        print(f"----- Constraint 19 created for busy period {h} -----")
        return constraint_19

    def create_constraint_20(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 20 for busy period {h} -----")
        constraint_20 = []
        for i, activations in s_i_h_for_h.items():
            for a in activations:
                for t in self.T_h[h]:
                    left_side = lpSum(t * x[i, a, j, t]
                                      for j in range(self.number_of_cores))
                    right_side = self.d_i_a[i][a] - 1
                    constraint_20.append(left_side <= right_side)
        print(f"----- Constraint 20 created for busy period {h} -----")
        return constraint_20

    def create_constraint_21(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 21 for busy period {h} -----")
        constraint_21 = []
        for j, t in product(range(self.number_of_cores), self.T_h[h]):
            constraint_21.append(
                lpSum(x[i, a, j, t] for i in s_i_h_for_h for a in s_i_h_for_h[i]) <= 1)
        print(f"----- Constraint 21 created for busy period {h} -----")
        return constraint_21

    def create_constraint_22(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 22 for busy period {h} -----")
        constraint_22 = []
        for i, activations in s_i_h_for_h.items():
            for k, b_activations in s_i_h_for_h.items():
                if i != k:
                    for a, b, j, l, t in product(activations, b_activations, range(self.number_of_cores), range(self.number_of_cores), self.T_h[h]):
                        if j != l:
                            constraint_22.append(
                                m[i, a, k, b] >= x[i, a, j, t] + x[k, b, l, t] - 1)
        print(f"----- Constraint 22 created for busy period {h} -----")
        return constraint_22

    def create_constraint_23(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 23 for busy period {h} -----")
        constraint_23 = []
        for i, activations in s_i_h_for_h.items():
            for k, b_activations in s_i_h_for_h.items():
                if i != k:
                    for a, b in product(activations, b_activations):
                        constraint_23.append(m[i, a, k, b] == m[k, b, i, a])
        print(f"----- Constraint 23 created for busy period {h} -----")
        return constraint_23

    def create_constraint_24(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w):
        print(f"----- Creating constraint 24 for busy period {h} -----")
        constraint_24 = []
        for i, activations in s_i_h_for_h.items():
            for a in activations:
                for j in range(self.number_of_cores):
                    for t in self.T_h[h]:
                        constraint_24.append(w[i, a] >= (
                            t * x[i, a, j, t]) - (a * self.taskset.period[i]) + 1)
        print(f"----- Constraint 24 created for busy period {h} -----")
        return constraint_24

    def createLpConstraints(self, h, x, m, w):
        # Extraction des données pour le busy period 'h'
        s_i_h_for_h = self.extract_s_i_h_for_h(h)
        r_i_a_h_for_h = self.extract_r_i_a_h_for_h(h, s_i_h_for_h)

        # Parallélisation de la création des contraintes
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(self.create_constraint_16, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_16",
                executor.submit(self.create_constraint_17, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_17",
                executor.submit(self.create_constraint_18, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_18",
                executor.submit(self.create_constraint_19, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_19",
                executor.submit(self.create_constraint_20, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_20",
                executor.submit(self.create_constraint_21, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_21",
                executor.submit(self.create_constraint_22, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_22",
                executor.submit(self.create_constraint_23, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_23",
                executor.submit(self.create_constraint_24, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w): "constraint_24",
            }

            results = {key: future.result() for future, key in futures.items()}

        return (results["constraint_16"], results["constraint_17"], results["constraint_18"],
                results["constraint_19"], results["constraint_20"], results["constraint_21"],
                results["constraint_22"], results["constraint_23"], results["constraint_24"])

    def schedule(self):
        print(
            f"-------------\nSolving RHMA")

        schedule = BusyPeriod()

        for h, busy_period in enumerate(self.busy_periods):
            prob = LpProblem(
                f"RHMA_Busy_Period_{h}", LpMinimize)
            print(
                f"-------------\nCreating variables for BP {h}/{len(self.busy_periods)} from {busy_period.start_time} to {busy_period.end_time}. total hyperperiod={self.hyperperiod}")

            x, m, w = self.createLpVariables(h)
            constraint_16, constraint_17, constraint_18, constraint_19, constraint_20, constraint_21, constraint_22, constraint_23, constraint_24 = self.createLpConstraints(
                h, x, m, w)

            for constraint in constraint_16:
                prob += constraint
            for constraint in constraint_17:
                prob += constraint
            for constraint in constraint_18:
                prob += constraint
            for constraint in constraint_19:
                prob += constraint
            for constraint in constraint_20:
                prob += constraint
            for constraint in constraint_21:
                prob += constraint
            for constraint in constraint_22:
                prob += constraint
            for constraint in constraint_23:
                prob += constraint
            for constraint in constraint_24:
                prob += constraint

            # Objective function
            interference_term = lpSum(m[i, a, k, b] for i in range(len(self.taskset)) for k in range(
                len(self.taskset)) for a in self.S_i_h[i, h] for b in self.S_i_h[k, h])

            response_time_term = lpSum(
                (1 / self.taskset.deadline[i]) * w[i, a] for i in range(len(self.taskset)) for a in self.S_i_h[i, h])

            # if maxI == 0
            if self.maxI != 0:
                interference_term /= self.maxI
            else:
                interference_term = 0

            prob += interference_term + response_time_term

            if self.solving_time_limit_MILP is not None and type(self.solving_time_limit_MILP) == int:
                if self.solver_name == "gurobi":
                    self.solver.options.append(
                        ("TimeLimit", self.solving_time_limit_MILP))

            print(
                f"-------------\nSolving BP {h}/{len(self.busy_periods)} from {busy_period.start_time} to {busy_period.end_time}")
            prob.solve(self.solver)

            # Checking if a solution is found
            if prob.status == LpStatusOptimal:
                total_utilization = 0
                busy_period_schedule = [[]
                                        for _ in range(self.number_of_cores)]

                for t in self.T_h[h]:
                    for i in range(len(self.taskset)):
                        for a in self.S_i_h[i, h]:
                            for j in range(self.number_of_cores):
                                if x[i, a, j, t].varValue == 1:
                                    busy_period_schedule[j].append(
                                        (t, i, a))
                                    total_utilization += 1

                busy_period_schedule = Scheduling(
                    schedule=busy_period_schedule, success=1, scheduler_name="RHMA")
                busy_period_schedule.add_total_utilization(
                    total_utilization=total_utilization)
                schedule.add_period(scheduling=busy_period_schedule)
                print(f"RHMA solution found for busy period {h}.")

            else:
                if self.busy_periods[h].success == 0:
                    print(
                        f'RHMA failed to find a solution for busy period. Cannot use CombinedScheduler instead, because it did not find one as well.')
                    return schedule
                else:
                    print(
                        f"RHMA failed to find a solution for busy period {h}. Using CombinedScheduler instead.")
                    schedule.add_period(scheduling=self.busy_periods[h])
                    total_utilization = self.busy_periods[h].total_utilization

            self.actual_utilization[h] = total_utilization/self.hyperperiod

        print("----- RHMA Scheduling Completed -----")
        return schedule
