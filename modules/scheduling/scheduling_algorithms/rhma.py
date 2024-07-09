import math
from pathlib import Path
from pulp import *
import time
from modules.scheduling.scheduling import Scheduling
from modules.scheduling.scheduling_algorithms.combined_scheduler import CombinedScheduler
from modules.utils.busy_period import BusyPeriod


class Rhma:
    def __init__(self, taskset, assignment, number_of_cores, start_time=0, end_time=None):
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.assignment = assignment
        self.number_of_cores = number_of_cores
        if end_time == None:
            end_time = self.hyperperiod

        self.start_time = start_time
        self.end_time = end_time
        # Parameters generated after assignment
        self.maxI = self.generate_max_I()
        self.o_i_j = self.generate_o_i_j()
        self.combined_scheduler = CombinedScheduler(taskset=self.taskset, assignment=self.assignment,
                                                    number_of_cores=self.number_of_cores, start_time=self.start_time,
                                                    end_time=self.end_time)
        self.busy_periods = self.combined_scheduler.schedule()

        # Parameters generated after busy period generation
        self.S_i_h = self.generate_S_i_h()
        self.R_i_a_h = self.generate_R_i_a_h()
        self.T_h = self.generate_T_h()
        self.d_i_a = self.taskset.absolute_deadline

        # Save parameters to file to analyse
        output_path = f"{Path(__file__).parent.parent.parent.parent}/output_parameters.txt"
        self.save_parameters_to_file(
            file_path=output_path)

    def output_parameters_to_str(self):
        output_res = "---------------------\n Parameters \n --------------\n"
        output_res += f"N: {self.taskset.N} \n"
        output_res += f"C: {self.taskset.wcet} \n"
        output_res += f"D: {self.taskset.deadline} \n"
        output_res += f"T: {self.taskset.period} \n"
        output_res += f"I: {self.taskset.interference} \n"
        output_res += f"Hyperperiod: {self.taskset.hyperperiod} \n"
        output_res += f"Activation: {self.taskset.activation} \n"
        output_res += f"Absolute deadline: {self.taskset.absolute_deadline} \n"
        output_res += f"maxI: {self.maxI} \n"
        output_res += f"o_i_j: {self.o_i_j} \n"
        output_res += f"Number of busy periods: {len(self.busy_periods)} \n"
        output_res += f"S_i_h: {self.S_i_h} \n"
        output_res += f"R_i_a_h: {self.R_i_a_h} \n"

        return output_res

    def save_parameters_to_file(self, file_path):
        output_res = self.output_parameters_to_str()
        with open(file_path, 'w') as file:
            file.write(output_res)

    def __str__(self):
        return self.__class__.__name__

    def generate_max_I(self):
        maxI = 0
        for i in range(len(self.taskset)):
            for j in range(len(self.taskset)):
                if i != j and self.assignment.find_task_core(i) != self.assignment.find_task_core(j):
                    if self.taskset[i].interference > 0 and self.taskset[j].interference > 0:
                        v_j_to_i = self.calculate_activation_pattern(
                            interfering_task_index=j, receiving_task_index=i)
                        for a in self.taskset.activation[i]:
                            maxI += v_j_to_i[a] * \
                                self.taskset[j].interference

        return maxI

    def calculate_activation_pattern(self, interfering_task_index, receiving_task_index):
        v_j_to_i = []
        for a in self.taskset.activation[receiving_task_index]:
            # TODO revoir ces parametres dans le papier pour être sure (les 3)
            activation_in_t = 1
            activation_start = a * self.taskset.period[receiving_task_index]
            # pas de -1 de la formule car python
            activation_end = (a + 1) * \
                self.taskset.period[receiving_task_index]
            for t in range(activation_start, activation_end):
                if t - self.taskset.period[interfering_task_index] * math.floor(t / self.taskset.period[interfering_task_index]) == 0:
                    activation_in_t += 1
            v_j_to_i.append(activation_in_t)
        return v_j_to_i

    def generate_o_i_j(self):
        o_i_j = []
        for task_index, task in enumerate(self.taskset):
            core_list = []
            for core in range(self.number_of_cores):
                if task_index in self.assignment[core]:
                    core_list.append(1)
                else:
                    core_list.append(0)
            o_i_j.append(core_list)
        return o_i_j

    def generate_S_i_h(self):
        S_i_h = [[[] for _ in range(len(self.busy_periods))]
                 for _ in range(len(self.taskset))]

        for i, task_period in enumerate(self.taskset.period):
            for a in self.taskset.activation[i]:
                activation_start = a * task_period
                for h, busy_period in enumerate(self.busy_periods):
                    if busy_period.start_time <= activation_start <= busy_period.end_time:
                        S_i_h[i][h].append(a)

        return S_i_h

    def generate_R_i_a_h(self):
        R_i_a_h = [[{} for _ in range(len(self.taskset.activation[i]))]
                   for i in range(len(self.taskset))]
        for i, task_period in enumerate(self.taskset.period):
            for a in self.taskset.activation[i]:
                activation_start = a * task_period
                activation_end = (a + 1) * task_period
                for h, busy_period in enumerate(self.busy_periods):
                    for t in range(busy_period.start_time, busy_period.end_time + 1):
                        if activation_start <= t < activation_end:
                            if h not in R_i_a_h[i][a]:
                                R_i_a_h[i][a][h] = []
                            R_i_a_h[i][a][h].append(t)
        return R_i_a_h

    def generate_R_i_a_h_list(self):
        R_i_a_h = [[[[] for _ in range(len(self.busy_periods))] for _ in range(
            len(self.taskset.activation[i]))] for i in range(len(self.taskset))]

        for i, task_period in enumerate(self.taskset.period):
            for a in self.taskset.activation[i]:
                activation_start = a * task_period
                activation_end = (a + 1) * task_period
                for h, busy_period in enumerate(self.busy_periods):
                    intersection_start = max(
                        activation_start, busy_period.start_time)
                    intersection_end = min(
                        activation_end, busy_period.end_time + 1)

                    R_i_a_h[i][a][h] = list(
                        range(intersection_start, intersection_end))
        return R_i_a_h

    def generate_T_h(self):
        T_h = []
        for busy_period in self.busy_periods:
            T_h.append(
                list(range(busy_period.start_time, busy_period.end_time + 1)))
        return T_h

    def schedule(self):
        schedule = BusyPeriod()

        for h, busy_period in enumerate(self.busy_periods):
            prob = LpProblem(
                f"RHMA_Busy_Period_{h}", LpMinimize)

            # Variables
            x = {}
            for i in range(len(self.taskset)):
                for a in self.S_i_h[i][h]:
                    for j in range(self.number_of_cores):
                        for t in self.R_i_a_h[i][a][h]:
                            x[i, a, j,
                              t] = LpVariable(f"x_{i}_{a}_{j}_{t}", cat='Binary')

            m = {}
            for i in range(len(self.taskset)):
                for k in range(len(self.taskset)):
                    for a in self.S_i_h[i][h]:
                        for b in self.S_i_h[k][h]:
                            m[i, a, k,
                              b] = LpVariable(f"m_{i}_{a}_{k}_{b}", cat='Binary')

            w = {}
            for i in range(len(self.taskset)):
                for a in self.S_i_h[i][h]:
                    w[i, a] = LpVariable(
                        f"w_{i}_{a}", lowBound=0, cat='Integer')

            # Constraints

            # Constraint 16
            for i in range(len(self.taskset)):
                for a in self.S_i_h[i][h]:
                    for j in range(self.number_of_cores):
                        if self.o_i_j[i][j] == 0:
                            for t in self.R_i_a_h[i][a][h]:
                                prob += x[i, a, j, t] == 0

            # Constraint 17
            for i in range(len(self.taskset)):
                for k in range(i + 1, len(self.taskset)):
                    for a in self.S_i_h[i][h]:
                        for b in self.S_i_h[k][h]:
                            if not set(self.R_i_a_h[i][a][h]).intersection(self.R_i_a_h[k][b][h]):
                                prob += m[i, a, k, b] == 0

            # Constraint 18
            for i in range(len(self.taskset)):
                for j in range(self.number_of_cores):
                    if self.o_i_j[i][j] == 1:
                        left_side = lpSum(x[i, a, j, t] for a in self.S_i_h[i][h]
                                          for t in self.R_i_a_h[i][a][h])

                        right_side = len(
                            self.S_i_h[i][h]) * self.taskset.wcet[i] * self.o_i_j[i][j]
                        right_side += lpSum(m[i, a, k, b] * self.taskset.interference[k] * self.o_i_j[i][j]
                                            for k in range(len(self.taskset)) if k != i
                                            for a in self.S_i_h[i][h]
                                            for b in self.S_i_h[k][h])
                        prob += left_side == right_side

            # Constraint 19
            for i in range(len(self.taskset)):
                for a in self.S_i_h[i][h]:
                    for j in range(self.number_of_cores):
                        if self.o_i_j[i][j] == 1:

                            left_side = lpSum(x[i, a, j, t]
                                              for t in self.R_i_a_h[i][a][h])

                            right_side = self.taskset.wcet[i] * \
                                self.o_i_j[i][j]
                            right_side += lpSum(m[i, a, k, b] * self.taskset.interference[k] * self.o_i_j[i][j]
                                                for k in range(len(self.taskset)) if k != i
                                                for b in self.S_i_h[k][h])
                            prob += left_side <= right_side

            # Constraint 20
            for i in range(len(self.taskset)):
                for a in self.S_i_h[i][h]:
                    left_side = lpSum(t * x[i, a, j, t] for j in range(self.number_of_cores)
                                      for t in self.R_i_a_h[i][a][h])
                    right_side = self.d_i_a[i][a] - 1
                    prob += left_side <= right_side

            # Constraint 21
            for j in range(self.number_of_cores):
                for t in self.T_h[h]:
                    prob += lpSum(x[i, a, j, t] for i in range(len(self.taskset))
                                  for a in self.S_i_h[i][h] if t in self.R_i_a_h[i][a][h]) <= 1

            # Constraint 22
            for i in range(len(self.taskset)):
                for k in range(len(self.taskset)):
                    if i != k:
                        for a in self.S_i_h[i][h]:
                            for b in self.S_i_h[k][h]:
                                for j in range(self.number_of_cores):
                                    for l in range(self.number_of_cores):
                                        if j != l:
                                            for t in set(self.R_i_a_h[i][a][h]).intersection(self.R_i_a_h[k][b][h]):
                                                prob += m[i, a, k, b] >= x[i,
                                                                           a, j, t] + x[k, b, l, t] - 1

            # Constraint 23
            for i in range(len(self.taskset)):
                for k in range(len(self.taskset)):
                    if i != k:
                        for a in self.S_i_h[i][h]:
                            for b in self.S_i_h[k][h]:
                                prob += m[i, a, k, b] == m[k, b, i, a]

            # Contrainte 24
            for i in range(len(self.taskset)):
                for a in self.S_i_h[i][h]:
                    for j in range(self.number_of_cores):
                        for t in self.R_i_a_h[i][a][h]:
                            prob += w[i, a] >= (t * x[i, a, j, t]) - \
                                (a * self.taskset.period[i]) + 1

            for i in range(len(self.taskset)):
                for k in range(len(self.taskset)):
                    if i != k:
                        for a in self.S_i_h[i][h]:
                            for b in self.S_i_h[k][h]:
                                # Contrainte factice
                                prob += m[i, a, k, b] <= 1

            # Objective function
            interference_term = lpSum(m[i, a, k, b] for i in range(len(self.taskset)) for k in range(
                len(self.taskset)) if i != k for a in self.S_i_h[i][h] for b in self.S_i_h[k][h])
            response_time_term = lpSum(
                (1 / self.taskset.deadline[i]) * w[i, a] for i in range(len(self.taskset)) for a in self.S_i_h[i][h])

            # if maxI == 0
            if self.maxI != 0:
                interference_term /= self.maxI
            else:
                interference_term = 0

            prob += interference_term + response_time_term

            # Solving the MILP problem
            prob.solve(GUROBI_CMD(msg=0, options=[
                       ("OutputFlag", 0), ("TimeLimit", 10)]))

            # Checking if a solution is found
            if prob.status == 1:
                busy_period_schedule = [[]
                                        for _ in range(self.number_of_cores)]

                for t in self.T_h[h]:
                    for i in range(len(self.taskset)):
                        for a in self.S_i_h[i][h]:
                            for j in range(self.number_of_cores):
                                if x[i, a, j, t].varValue == 1:
                                    busy_period_schedule[j].append(
                                        (t, i, a))

                busy_period_schedule = Scheduling(
                    schedule=busy_period_schedule, success=1, scheduler_name="RHMA")
                schedule.add_period(scheduling=busy_period_schedule)

            else:
                print(
                    f"RHMA failed to find a solution for busy period {h}. Using CombinedScheduler instead.")
                schedule.add_period(scheduling=self.busy_periods[h])

            if prob.status == 1:
                print(schedule[h])
                time.sleep(100)

        return schedule
