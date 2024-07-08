import numpy
import math
from pulp import *
import time
from modules.scheduling.scheduling import Scheduling
from modules.scheduling.scheduling_algorithms.combined_scheduler import CombinedScheduler
from modules.utils.busy_period_generator import BusyPeriodGenerator


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
        # Parameters from assignment
        self.maxI = self.generate_max_I()
        self.o_i_j = self.generate_o_i_j()
        self.combined_scheduler = CombinedScheduler(taskset=self.taskset, assignment=self.assignment,
                                                    number_of_cores=self.number_of_cores, start_time=self.start_time, end_time=self.end_time)
        self.busy_periods = self.combined_scheduler.schedule()
        self.S_i_h = self.generate_S_i_h()
        self.R_i_a_h = self.generate_R_i_a_h()
        self.T_h = self.generate_T_h()

    def __str__(self):
        return self.__class__.__name__

    def generate_max_I(self):
        maxI = 0
        for i in range(len(self.taskset.period)):
            for j in range(len(self.taskset.period)):
                if i != j and self.assignment.find_task_core(self.taskset[i]) != self.assignment.find_task_core(self.taskset[j]):
                    if max(self.taskset[i].interference) > 0 and max(self.taskset[j].interference) > 0:
                        v_j_to_i = self.calculate_activation_pattern(
                            interfering_task_index=j, receiving_task_index=i)
                        for a in self.taskset.activation[i]:
                            maxI += v_j_to_i[a] * \
                                max(self.taskset[j].interference)

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
        for core in range(self.number_of_cores):
            core_list = []
            for task in self.taskset:
                if task in self.assignment[core]:
                    core_list.append(1)
                else:
                    core_list.append(0)
            o_i_j.append(core_list)
        return o_i_j

    def generate_S_i_h(self):
        S_i_h = [[[] for _ in range(len(self.busy_periods))]
                 for _ in range(len(self.taskset.period))]

        for i, task_period in enumerate(self.taskset.period):
            for a in self.taskset.activation[i]:
                activation_start = a * task_period
                for h, busy_period in enumerate(self.busy_periods):
                    if busy_period.start_time <= activation_start <= busy_period.end_time:
                        S_i_h[i][h].append(a)

        return S_i_h

    def generate_R_i_a_h(self):
        R_i_a_h = [[{} for _ in range(len(self.taskset.activation[i]))]
                   for i in range(len(self.taskset.period))]
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

    def generate_T_h(self):
        T_h = []
        for busy_period in self.busy_periods:
            T_h.append(
                list(range(busy_period.start_time, busy_period.end_time + 1)))
        return T_h

    def schedule(self):
        pass
