# interference_generation.py

import numpy
import math

class InterferenceGeneration:
    def __init__(self, number_of_taskset , number_of_task_in_taskset, interference_factor, probability_factor):
        self.number_of_taskset = number_of_taskset
        self.number_of_task_in_taskset = number_of_task_in_taskset
        self.interference_factor = interference_factor
        self.probability_factor = probability_factor

    def gen_interference(self, wcets):
        interferences = numpy.zeros((self.number_of_taskset, self.number_of_task_in_taskset, self.number_of_task_in_taskset))
        for _set in range(self.number_of_taskset):
            interferences[_set] = self.gen_taskset_interference(wcets[_set])
        return interferences

    def gen_taskset_interference(self, wcets):
        cache_interference = numpy.zeros((self.number_of_task_in_taskset, self.number_of_task_in_taskset))
        for task_i in range(self.number_of_task_in_taskset):
            for task_j in range(task_i + 1, self.number_of_task_in_taskset):
                random_inter = numpy.random.uniform(0, 1)
                has_interference = 1 if random_inter < self.probability_factor else 0
                cache_interference[task_i][task_j] = has_interference * math.floor(self.interference_factor * 0.5 * min(wcets[task_i], wcets[task_j]))
                cache_interference[task_j][task_i] = cache_interference[task_i][task_j]
        for i in range(self.number_of_task_in_taskset):
            cache_interference[i, i] = 0
        return cache_interference
