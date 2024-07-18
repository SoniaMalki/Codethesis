import random
import numpy


class DeadlineGenerator:
    def __init__(self):
        pass

    def generate_deadlines(self, periods, wcets, deadline_option):
        if deadline_option == "eq_period":
            deadlines = [period for period in periods]
        elif deadline_option == "leq_period":
            deadlines = []
            for taskset_index in range(len(periods)):
                taskset_deadlines = []
                for task_index in range(len(periods[taskset_index])):
                    # Ensure deadline is greater than or equal to WCET
                    deadline = random.randint(
                        int(wcets[taskset_index][task_index]), periods[taskset_index][task_index])
                    taskset_deadlines.append(deadline)
                deadlines.append(taskset_deadlines)
        return numpy.array(deadlines)
