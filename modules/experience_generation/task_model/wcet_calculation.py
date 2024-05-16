# wcet_calculation.py

import numpy
import math

class WCETCalculation:
    def __init__(self, number_of_taskset, number_of_task_in_taskset):
        self.number_of_taskset = number_of_taskset
        self.number_of_task_in_taskset = number_of_task_in_taskset

    def calculate_wcets(self, periods, utilizations):
        wcets = numpy.zeros((self.number_of_taskset, self.number_of_task_in_taskset))
        for set_index in range(self.number_of_taskset):
            for task_index in range(self.number_of_task_in_taskset):
                wcets[set_index][task_index] = max(1, math.floor(periods[set_index][task_index] * utilizations[set_index][task_index]))
        return wcets
