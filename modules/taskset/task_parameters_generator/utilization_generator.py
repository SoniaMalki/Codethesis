
import numpy

class UtilizationGenerator:
    def __init__(self, taskset_count, tasks_per_taskset, max_utilization):
        self.taskset_count = taskset_count
        self.tasks_per_taskset = tasks_per_taskset
        self.max_utilization = max_utilization

    def generate_utilizations(self):
        if self.tasks_per_taskset == 1:
            return numpy.tile(numpy.array([self.max_utilization]), [self.taskset_count, 1])

        floor_max_utilization = numpy.floor(self.max_utilization)
        remaining_utilization = self.max_utilization
        step = 1 if floor_max_utilization < (floor_max_utilization - self.tasks_per_taskset + 1) else -1
        stepwise_decrease = remaining_utilization - numpy.arange(floor_max_utilization, (floor_max_utilization - self.tasks_per_taskset + 1) + step, step)
        step = 1 if (floor_max_utilization + self.tasks_per_taskset) < (floor_max_utilization - self.tasks_per_taskset + 1) else -1
        stepwise_increase = numpy.arange((floor_max_utilization + self.tasks_per_taskset), (floor_max_utilization + 1) + step, step) - remaining_utilization

        epsilon = numpy.finfo(float).tiny
        infinity = numpy.finfo(float).max

        weight_matrix = numpy.zeros((self.tasks_per_taskset, self.tasks_per_taskset + 1))
        weight_matrix[0, 1] = infinity
        transition_probabilities = numpy.zeros((self.tasks_per_taskset - 1, self.tasks_per_taskset))

        for i in numpy.arange(2, (self.tasks_per_taskset + 1)):
            tmp1 = weight_matrix[i - 2, numpy.arange(1, (i + 1))] * stepwise_decrease[numpy.arange(0, i)] / float(i)
            tmp2 = weight_matrix[i - 2, numpy.arange(0, i)] * stepwise_increase[numpy.arange((self.tasks_per_taskset - i), self.tasks_per_taskset)] / float(i)
            weight_matrix[i - 1, numpy.arange(1, (i + 1))] = tmp1 + tmp2
            tmp3 = weight_matrix[i - 1, numpy.arange(1, (i + 1))] + epsilon
            tmp4 = numpy.array((stepwise_increase[numpy.arange((self.tasks_per_taskset - i), self.tasks_per_taskset)] > stepwise_decrease[numpy.arange(0, i)]))
            transition_probabilities[i - 2, numpy.arange(0, i)] = (tmp2 / tmp3) * tmp4 + (1 - tmp1 / tmp3) * (numpy.logical_not(tmp4))

        utilization_matrix = numpy.zeros((self.tasks_per_taskset, self.taskset_count))
        random_thresholds = numpy.random.uniform(size=(self.tasks_per_taskset - 1, self.taskset_count))
        random_scalars = numpy.random.uniform(size=(self.tasks_per_taskset - 1, self.taskset_count))
        remaining_utilization = numpy.repeat(remaining_utilization, self.taskset_count)
        remaining_tasks = numpy.repeat(int(floor_max_utilization + 1), self.taskset_count)
        sum_utilization = numpy.repeat(0, self.taskset_count)
        product_scalars = numpy.repeat(1, self.taskset_count)

        for i in numpy.arange(self.tasks_per_taskset - 1, 0, -1):
            is_threshold_met = (random_thresholds[(self.tasks_per_taskset - i) - 1, ...] <= transition_probabilities[i - 1, remaining_tasks - 1])
            scaled_random = random_scalars[(self.tasks_per_taskset - i) - 1, ...] ** (1 / float(i))
            sum_utilization = sum_utilization + (1 - scaled_random) * product_scalars * remaining_utilization / float(i + 1)
            product_scalars = scaled_random * product_scalars
            utilization_matrix[(self.tasks_per_taskset - i) - 1, ...] = sum_utilization + product_scalars * is_threshold_met
            remaining_utilization = remaining_utilization - is_threshold_met
            remaining_tasks = remaining_tasks - is_threshold_met

        utilization_matrix[self.tasks_per_taskset - 1, ...] = sum_utilization + product_scalars * remaining_utilization
        
        for i in range(0, self.taskset_count):
            utilization_matrix[..., i] = utilization_matrix[numpy.random.permutation(self.tasks_per_taskset), i]
        print(utilization_matrix)
        return numpy.transpose(utilization_matrix)
