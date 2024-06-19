
import numpy
import math

class WCETCalculator:
    def __init__(self, taskset_count, tasks_per_taskset):
        self.taskset_count = taskset_count
        self.tasks_per_taskset = tasks_per_taskset

    def compute_wcets(self, task_periods, task_utilizations):
        calculated_wcets = numpy.zeros((self.taskset_count, self.tasks_per_taskset))
        for taskset_index in range(self.taskset_count):
            for task_index_within_set in range(self.tasks_per_taskset):
                calculated_wcets[taskset_index][task_index_within_set] = max(1, math.floor(
                    task_periods[taskset_index][task_index_within_set] * task_utilizations[taskset_index][task_index_within_set]
                ))
        return calculated_wcets
