
import numpy
import random

class PeriodGenerator:
    def __init__(self, taskset_count, tasks_per_taskset, prime_matrix):
        self.taskset_count = taskset_count
        self.tasks_per_taskset = tasks_per_taskset
        #self.granularity = granularity
        self.prime_matrix = prime_matrix

    def generate_periods(self):
        generated_periods = self.generate_periods_from_matrix()
        generated_periods = numpy.array(generated_periods)

        #generated_periods = numpy.floor(generated_periods / self.granularity) * self.granularity
        return generated_periods

    def generate_single_period(self):
        period = 1
        for prime_factors in self.prime_matrix:
            random_index = random.randint(0, len(prime_factors) - 1)
            period *= prime_factors[random_index]
        return period

    def generate_periods_from_matrix(self):
        periods_array = []
        for _ in range(self.taskset_count):
            periods = [self.generate_single_period() for _ in range(self.tasks_per_taskset)]
            periods_array.append(periods)
        return periods_array
