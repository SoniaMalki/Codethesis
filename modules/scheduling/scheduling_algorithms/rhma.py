import math
import dill
from pathlib import Path
from itertools import product
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import numpy as np
from modules.scheduling.scheduling import Scheduling
from modules.scheduling.scheduling_algorithms.combined_scheduler import CombinedScheduler
from modules.utils.busy_period import BusyPeriod
import gurobipy as gp
from gurobipy import GRB  # Importe le module gurobipy


class Rhma:
    def __init__(self, taskset, assignment, number_of_cores, scheduling_options, start_time=0, end_time=None):
        # print("----- Initializing RHMA -----")
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.assignment = assignment
        self.number_of_cores = number_of_cores
        self.scheduling_options = scheduling_options

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

        self.test_mode = self.scheduling_options.get("test_mode", False)
        if self.test_mode:
            self.seed = self.scheduling_options.get("seed", 42)
            self.threads = 1

        if self.solver_name == "gurobi":
            self.param = []
            if self.test_mode:
                self.param.append(('OutputFlag', 0))
                self.param.append(('Seed', self.seed))

            else:
                self.param.append(('OutputFlag', 0))
                self.param.append(('Threads', self.threads))
        else:
            raise ValueError(
                f"Solveur non supporté: {self.solver_name}. Choisissez 'gurobi'.")

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

        w = {(i, a): self.model.addVar(lb=0, vtype=GRB.INTEGER, name=f'w_{i}_{a}')
             for i in range(len(self.taskset)) for a in self.S_i_h[i, h]}

        x = {(i, a, j, t): self.model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{a}_{j}_{t}')
             for i in range(len(self.taskset))
             for a in self.S_i_h[i, h]
             for j, t in product(
                 range(self.number_of_cores),
                 self.T_h[h]
        )
        }

        m = {(i, a, k, b): self.model.addVar(vtype=GRB.BINARY, name=f'm_{i}_{a}_{k}_{b}')
             for i, k in product(range(len(self.taskset)), repeat=2)
             for a in self.S_i_h[i, h]
             for b in self.S_i_h[k, h]
             }

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

    def calculate_estimated_size(self, s_i_h_for_h, h):
        """Calcule estimated_size pour toutes les contraintes en une fois."""
        size = {
            "constraint_16": 0,
            "constraint_17": 0,
            "constraint_18": 0,
            "constraint_19": 0,
            "constraint_20": 0,
            "constraint_21": 0,
            "constraint_22": 0,
            "constraint_23": 0,
            "constraint_24": 0
        }

        for i, activations in s_i_h_for_h.items():
            size["constraint_16"] += len(activations) * \
                self.number_of_cores * len(self.T_h[h])
            size["constraint_18"] += len(activations) * self.number_of_cores
            size["constraint_19"] += len(activations) * self.number_of_cores
            size["constraint_20"] += len(activations) * len(self.T_h[h])
            size["constraint_24"] += len(activations) * \
                self.number_of_cores * len(self.T_h[h])

            for k, b_activations in s_i_h_for_h.items():
                if i != k:
                    size["constraint_17"] += len(activations) * \
                        len(b_activations)
                    size["constraint_22"] += len(activations) * len(
                        b_activations) * self.number_of_cores * (self.number_of_cores - 1) * len(self.T_h[h])
                    size["constraint_23"] += len(activations) * \
                        len(b_activations)

        size["constraint_21"] = self.number_of_cores * len(self.T_h[h])

        return size

    def create_constraint_16(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 16 for busy period {h} -----")

        constraint_16 = np.empty((estimated_size,), dtype=object)
        index = 0
        for i, activations in s_i_h_for_h.items():
            for a in activations:
                for j in range(self.number_of_cores):
                    for t in self.T_h[h]:
                        if self.o_i_j[i, j] == 0:
                            constraint_16[index] = x[i, a, j, t] == 0
                            index += 1
        print(f"----- Constraint 16 created for busy period {h} -----")
        return constraint_16[:index]

    def create_constraint_17(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 17 for busy period {h} -----")

        constraint_17 = np.empty((estimated_size,), dtype=object)
        index = 0
        for i, activations in s_i_h_for_h.items():
            for k in range(i + 1, len(s_i_h_for_h)):
                activations_i = s_i_h_for_h[i]
                activations_k = s_i_h_for_h[k]
                for a, b in product(activations_i, activations_k):
                    if not np.intersect1d(r_i_a_h_for_h[i][a], r_i_a_h_for_h[k][b]).size:
                        constraint_17[index] = m[i, a, k, b] == 0
                        index += 1
        print(f"----- Constraint 17 created for busy period {h} -----")
        return constraint_17[:index]

    def create_constraint_18(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 18 for busy period {h} -----")

        constraint_18 = np.empty((estimated_size,), dtype=object)
        index = 0
        for i, activations in s_i_h_for_h.items():
            for j in range(self.number_of_cores):
                if activations:
                    left_side = gp.quicksum(x[i, a, j, t]
                                            for a in activations for t in r_i_a_h_for_h[i][a])
                    right_side = len(activations) * \
                        self.taskset.wcet[i] * self.o_i_j[i, j]

                    right_side += gp.quicksum(m[i, a, k, b] * self.taskset.single_interference[k] * self.o_i_j[i, j]
                                              for k, b_activations in s_i_h_for_h.items() if k != i and self.o_i_j[i, j] != self.o_i_j[k, j] and self.taskset.single_interference[k] > 0 and self.taskset.single_interference[i] > 0
                                              for a in activations for b in b_activations)
                    constraint_18[index] = left_side == right_side
                    index += 1

        print(f"----- Constraint 18 created for busy period {h} -----")
        return constraint_18[:index]

    def create_constraint_19(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 19 for busy period {h} -----")

        constraint_19 = np.empty((estimated_size,), dtype=object)
        index = 0
        for i, activations in s_i_h_for_h.items():
            for a in activations:
                for j in range(self.number_of_cores):
                    if activations:
                        left_side = gp.quicksum(x[i, a, j, t]
                                                for t in r_i_a_h_for_h[i][a])
                        right_side = self.taskset.wcet[i] * self.o_i_j[i, j]

                        right_side += gp.quicksum(m[i, a, k, b] * self.taskset.single_interference[k] * self.o_i_j[i, j]
                                                  for k, b_activations in s_i_h_for_h.items() if k != i and self.o_i_j[i, j] != self.o_i_j[k, j] and self.taskset.single_interference[k] > 0 and self.taskset.single_interference[i] > 0
                                                  for b in b_activations)

                        constraint_19[index] = left_side == right_side
                        index += 1
        print(f"----- Constraint 19 created for busy period {h} -----")
        return constraint_19[:index]

    def create_constraint_20(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 20 for busy period {h} -----")

        constraint_20 = np.empty((estimated_size,), dtype=object)
        index = 0
        for i, activations in s_i_h_for_h.items():
            for a in activations:
                for t in self.T_h[h]:
                    left_side = gp.quicksum(t * x[i, a, j, t]
                                            for j in range(self.number_of_cores))
                    right_side = self.d_i_a[i][a] - 1
                    constraint_20[index] = left_side <= right_side
                    index += 1
        print(f"----- Constraint 20 created for busy period {h} -----")
        return constraint_20[:index]

    def create_constraint_21(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 21 for busy period {h} -----")

        constraint_21 = np.empty((estimated_size,), dtype=object)
        index = 0
        for j, t in product(range(self.number_of_cores), self.T_h[h]):
            constraint_21[index] = gp.quicksum(
                x[i, a, j, t] for i in s_i_h_for_h for a in s_i_h_for_h[i]) <= 1
            index += 1
        print(f"----- Constraint 21 created for busy period {h} -----")
        return constraint_21[:index]

    def create_constraint_22(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 22 for busy period {h} -----")

        constraint_22 = np.empty((estimated_size,), dtype=object)
        index = 0
        for i, activations in s_i_h_for_h.items():
            for k, b_activations in s_i_h_for_h.items():
                if i != k:
                    for a, b, j, l, t in product(activations, b_activations, range(self.number_of_cores), range(self.number_of_cores), self.T_h[h]):
                        if j != l:
                            constraint_22[index] = m[i, a, k,
                                                     b] >= x[i, a, j, t] + x[k, b, l, t] - 1
                            index += 1
        print(f"----- Constraint 22 created for busy period {h} -----")
        return constraint_22[:index]

    def create_constraint_23(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 23 for busy period {h} -----")

        constraint_23 = np.empty((estimated_size,), dtype=object)
        index = 0
        for i, activations in s_i_h_for_h.items():
            for k, b_activations in s_i_h_for_h.items():
                if i != k:
                    for a, b in product(activations, b_activations):
                        constraint_23[index] = m[i, a, k, b] == m[k, b, i, a]
                        index += 1
        print(f"----- Constraint 23 created for busy period {h} -----")
        return constraint_23[:index]

    def create_constraint_24(self, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_size):
        print(f"----- Creating constraint 24 for busy period {h} -----")

        constraint_24 = np.empty((estimated_size,), dtype=object)
        index = 0
        for i, activations in s_i_h_for_h.items():
            for a in activations:
                for j in range(self.number_of_cores):
                    for t in self.T_h[h]:
                        constraint_24[index] = w[i, a] >= (
                            t * x[i, a, j, t]) - (a * self.taskset.period[i]) + 1
                        index += 1
        print(f"----- Constraint 24 created for busy period {h} -----")
        return constraint_24[:index]


    def createLpConstraints(self, h, x, m, w):
        s_i_h_for_h = self.extract_s_i_h_for_h(h)
        r_i_a_h_for_h = self.extract_r_i_a_h_for_h(h, s_i_h_for_h)

        # Calculer estimated_size pour toutes les contraintes
        estimated_sizes = self.calculate_estimated_size(s_i_h_for_h, h)

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(self.create_constraint_16, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_16"]): "constraint_16",
                executor.submit(self.create_constraint_17, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_17"]): "constraint_17",
                executor.submit(self.create_constraint_18, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_18"]): "constraint_18",
                executor.submit(self.create_constraint_19, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_19"]): "constraint_19",
                executor.submit(self.create_constraint_20, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_20"]): "constraint_20",
                executor.submit(self.create_constraint_21, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_21"]): "constraint_21",
                executor.submit(self.create_constraint_22, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_22"]): "constraint_22",
                executor.submit(self.create_constraint_23, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_23"]): "constraint_23",
                executor.submit(self.create_constraint_24, s_i_h_for_h, r_i_a_h_for_h, h, x, m, w, estimated_sizes["constraint_24"]): "constraint_24",
            }

            results = {key: future.result() for future, key in futures.items()}

        return (results["constraint_16"], results["constraint_17"], results["constraint_18"],
                results["constraint_19"], results["constraint_20"], results["constraint_21"],
                results["constraint_22"], results["constraint_23"], results["constraint_24"])

    def add_constraints(self, prob, constraints_dict):
        for constraint_name, constraints in constraints_dict.items():
            constraint_id = 0
            num_constraints = len(constraints)
            # Détermine le nombre de zéros nécessaires pour l'indexation
            zero_padding = len(str(num_constraints - 1))

            while constraint_id < num_constraints:
                # Formate le constraint_id avec le bon nombre de zéros
                formatted_id = f"{constraint_id:0{zero_padding}}"
                self.model.addConstr(
                    constraints[constraint_id], name=f"{constraint_name}_{formatted_id}")
                constraint_id += 1

    def schedule(self):
        print(
            f"-------------\nSolving RHMA")

        schedule = BusyPeriod()
        if len(self.busy_periods) <= 1:
            print(
                "CombinedScheduler failed to divide the hyperperiod into busy periods. RHMA will not run.")
            return schedule

        for h, busy_period in enumerate(self.busy_periods):
            print(
                f"-------------\nCreating variables for BP {h}/{len(self.busy_periods)} from {busy_period.start_time} to {busy_period.end_time}. total hyperperiod={self.hyperperiod}")
            # Création du modèle
            self.model = gp.Model(f"RHMA_Busy_Period_{h}")
            for param in self.param:
                self.model.setParam(*param)

            x, m, w = self.createLpVariables(h)
            constraints = self.createLpConstraints(h, x, m, w)
            if constraints is None:
                return schedule
            constraint_16, constraint_17, constraint_18, constraint_19, constraint_20, constraint_21, constraint_22, constraint_23, constraint_24 = constraints

            # Exemple d'utilisation avec votre série de contraintes
            constraints_dict = {
                "constraint_16": constraint_16,
                "constraint_17": constraint_17,
                "constraint_18": constraint_18,
                "constraint_19": constraint_19,
                "constraint_20": constraint_20,
                "constraint_21": constraint_21,
                "constraint_22": constraint_22,
                "constraint_23": constraint_23,
                "constraint_24": constraint_24
            }

            # Appel de la fonction
            print("----Adding constraints to the model----")
            self.add_constraints(self.model, constraints_dict)
            print("----Finished adding the constraint to the model----")

            print("----Creating objective function----")
            # Objective function
            interference_term = gp.quicksum(m[i, a, k, b] for i in range(len(self.taskset)) for k in range(
                len(self.taskset)) for a in self.S_i_h[i, h] for b in self.S_i_h[k, h])

            response_time_term = gp.quicksum(
                (1 / self.taskset.deadline[i]) * w[i, a] for i in range(len(self.taskset)) for a in self.S_i_h[i, h])

            if self.maxI != 0:
                interference_term /= self.maxI
            else:
                interference_term = 0
            print("----Objective function created----")

            print("----Adding objective function to the model----")
            self.model.setObjective(
                interference_term + response_time_term, GRB.MINIMIZE)

            if self.solving_time_limit_MILP is not None and type(self.solving_time_limit_MILP) == int:
                self.model.setParam(GRB.Param.TimeLimit,
                                    self.solving_time_limit_MILP)

            print("----Added objective function to the model----")

            # Mécanisme de réessai pour résoudre le modèle
            max_retries = 100
            retries = 0
            success = False

            while retries < max_retries and not success:
                try:
                    print(
                        f"-------------\nSolving BP {h}/{len(self.busy_periods)} from {busy_period.start_time} to {busy_period.end_time}")
                    # self.model.write(f"modele_rhma_gurobipy_{h}.lp")
                    # self.model.write(f"modele_rhma_gurobipy_{h}.mps")
                    self.model.optimize()
                    print(
                        f"-------------\nFinished BP solving-------------\n")

                    # Checking if a solution is found
                    if self.model.status == GRB.OPTIMAL:
                        total_utilization = 0
                        busy_period_schedule = [[]
                                                for _ in range(self.number_of_cores)]

                        for t in self.T_h[h]:
                            for i in range(len(self.taskset)):
                                for a in self.S_i_h[i, h]:
                                    for j in range(self.number_of_cores):
                                        if x[i, a, j, t].X == 1:
                                            busy_period_schedule[j].append(
                                                (t, i, a))
                                            total_utilization += 1

                        busy_period_schedule = Scheduling(
                            schedule=busy_period_schedule, success=1, scheduler_name="RHMA")
                        busy_period_schedule.add_total_utilization(
                            total_utilization=total_utilization)
                        schedule.add_period(scheduling=busy_period_schedule)
                        print(f"RHMA solution found for busy period {h}.")
                        success = True

                    else:
                        if self.busy_periods[h].success == 0:
                            print(
                                f'RHMA failed to find a solution for busy period. Cannot use CombinedScheduler instead, because it did not find one as well.')
                            return schedule
                        else:
                            print(
                                f"RHMA failed to find a solution for busy period {h}. Using CombinedScheduler instead.")
                            schedule.add_period(
                                scheduling=self.busy_periods[h])
                            total_utilization = self.busy_periods[h].total_utilization
                        success = True

                    if type(self.actual_utilization) == float:
                        self.actual_utilization = [np.nan]
                    self.actual_utilization[h] = total_utilization / \
                        self.hyperperiod

                except gp.GurobiError:
                    retries += 1
                    print(f"Gurobi error, retrying {retries}/{max_retries}")
                    success = False

            if retries >= max_retries:
                # Raise the exception if the limit is reached
                raise gp.GurobiError(
                    "Gurobi failed to solve after multiple attempts.")

        print("----- RHMA Scheduling Completed -----")
        return schedule
