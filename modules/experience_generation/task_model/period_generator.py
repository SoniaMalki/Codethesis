
import numpy
import random

class PeriodGenerator:
    def __init__(self, taskset_count, tasks_per_taskset, min_period, max_period, granularity, period_generation_method, prime_matrix):
        self.taskset_count = taskset_count
        self.tasks_per_taskset = tasks_per_taskset
        self.min_period = min_period
        self.max_period = max_period
        self.granularity = granularity
        self.period_generation_method = period_generation_method
        self.prime_matrix = prime_matrix

    def generate_periods(self):
        if self.period_generation_method == "logunif":
            generated_periods = numpy.exp(numpy.random.uniform(low=numpy.log(self.min_period), high=numpy.log(self.max_period * self.granularity), size=(self.taskset_count, self.tasks_per_taskset)))
        elif self.period_generation_method == "unif":
            generated_periods = numpy.random.uniform(low=self.min_period, high=(self.max_period + self.granularity), size=(self.taskset_count, self.tasks_per_taskset))
        elif type(self.period_generation_method) == list:
            assert self.taskset_count == 1
            generated_periods = [random.choice(self.period_generation_method) for _ in range(self.tasks_per_taskset)]
            generated_periods = numpy.array(generated_periods)
            generated_periods.shape = (1, self.tasks_per_taskset)
            
        elif self.period_generation_method == "matrixM":
            generated_periods = self.generate_periods_from_matrix()
            generated_periods = numpy.array(generated_periods)
        else:
            return None
        generated_periods = numpy.floor(generated_periods / self.granularity) * self.granularity
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
