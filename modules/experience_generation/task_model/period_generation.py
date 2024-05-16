# period_generation.py

import numpy
import random

class PeriodGeneration:
    def __init__(self, number_of_taskset, number_of_task_in_taskset, period_min, period_max, granularity, method_of_period_generation, matrixM):
        self.number_of_taskset = number_of_taskset
        self.number_of_task_in_taskset = number_of_task_in_taskset
        self.period_min = period_min
        self.period_max = period_max
        self.granularity = granularity
        self.method_of_period_generation = method_of_period_generation
        self.matrixM = matrixM

    def gen_periods(self):
        if self.method_of_period_generation == "logunif":
            periods = numpy.exp(numpy.random.uniform(low=numpy.log(self.period_min), high=numpy.log(self.period_max + self.granularity), size=(self.number_of_taskset, self.number_of_task_in_taskset)))
        elif self.method_of_period_generation == "unif":
            periods = numpy.random.uniform(low=self.period_min, high=(self.period_max + self.granularity), size=(self.number_of_taskset, self.number_of_task_in_taskset))
        elif type(self.method_of_period_generation) == list:
            if self.random_generation:
                assert self.number_of_taskset == 1
                periods = [random.choice(self.method_of_period_generation) for _ in range(self.number_of_task_in_taskset)]
            else:
                periods = self.method_of_period_generation
            periods = numpy.array(periods)
            periods.shape = (1, self.number_of_task_in_taskset)
        elif self.method_of_period_generation == "matrixM":
            periods = self.generate_periods()
            periods = numpy.array(periods)
        else:
            return None
        periods = numpy.floor(periods / self.granularity) * self.granularity
        return periods

    def generate_single_period(self):
        period = 1
        for line in self.matrixM:
            j = random.randint(0, len(line) - 1)
            period *= line[j]
        return period

    def generate_periods(self):
        periods_array = []
        for _ in range(self.number_of_taskset):
            periods = [self.generate_single_period() for _ in range(self.number_of_task_in_taskset)]
            periods_array.append(periods)
        return periods_array
