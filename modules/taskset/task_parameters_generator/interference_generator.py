
from asyncio import tasks
import numpy
import math


class InterferenceGenerator:
    def __init__(self, taskset_count, tasks_per_taskset, interference_factor, probability_factor):
        self.taskset_count = taskset_count
        self.tasks_per_taskset = tasks_per_taskset
        self.interference_factor = interference_factor
        self.probability_factor = probability_factor

    def generate_interference(self, task_wcets):
        interferences = numpy.zeros(
            (self.taskset_count, self.tasks_per_taskset, self.tasks_per_taskset))
        single_interference = numpy.zeros(
            (self.taskset_count, self.tasks_per_taskset))
        for taskset_index in range(self.taskset_count):
            interferences[taskset_index], single_interference[taskset_index] = self.generate_taskset_interference(
                task_wcets[taskset_index])
        return interferences, single_interference

    def generate_taskset_interference(self, task_wcets):
        taskset_interference_matrix = numpy.zeros(
            (self.tasks_per_taskset, self.tasks_per_taskset))
        for task_index_i in range(self.tasks_per_taskset):
            for task_index_j in range(task_index_i + 1, self.tasks_per_taskset):
                random_value = numpy.random.uniform(0, 1)
                interference_occurs = 1 if random_value < self.probability_factor else 0
                taskset_interference_matrix[task_index_i][task_index_j] = interference_occurs * math.floor(
                    self.interference_factor * 0.5 *
                    min(task_wcets[task_index_i], task_wcets[task_index_j])
                )
                taskset_interference_matrix[task_index_j][task_index_i] = taskset_interference_matrix[task_index_i][task_index_j]

        for i in range(self.tasks_per_taskset):
            taskset_interference_matrix[i, i] = 0
        taskset_interference = numpy.array([max(row)
                                            for row in taskset_interference_matrix])
        return taskset_interference_matrix, taskset_interference
