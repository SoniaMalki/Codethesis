import numpy
from modules.experience_generation.task_model.utilization_generator import UtilizationGenerator
from modules.experience_generation.task_model.period_generator import PeriodGenerator
from modules.experience_generation.task_model.wcet_calculator import WCETCalculator
from modules.experience_generation.task_model.interference_generator import InterferenceGenerator
from modules.experience_generation.taskset_set import TasksetSet
from modules.taskset import Taskset
from modules.experience_generation.task_model.prime_matrix_generator import PrimeMatrixGenerator



class TasksetSetGenerator:
    def __init__(self, taskset_set_number, taskset_count, min_period, max_period, granularity, 
                tasks_per_taskset, interference_factor, probability_factor, period_generation_method, 
                max_utilization):
        self.taskset_set_number = taskset_set_number
        self.taskset_count = taskset_count
        self.min_period = min_period
        self.max_period = max_period
        self.granularity = granularity
        self.tasks_per_taskset = tasks_per_taskset
        self.interference_factor = interference_factor
        self.probability_factor = probability_factor
        self.period_generation_method = period_generation_method
        self.max_utilization = max_utilization

        self.prime_matrix_generator = PrimeMatrixGenerator(max_hyperperiod=100000, max_prime=20, gen_limit_exponent=2)

        self.prime_matrix = self.prime_matrix_generator.prime_matrix

        self.utilization_generator = UtilizationGenerator(self.taskset_count, self.tasks_per_taskset, self.max_utilization)
        self.period_generator = PeriodGenerator(self.taskset_count, self.tasks_per_taskset, self.min_period, self.max_period, self.granularity, self.period_generation_method, self.prime_matrix)
        self.wcet_calculator = WCETCalculator(self.taskset_count, self.tasks_per_taskset)
        self.interference_generator = InterferenceGenerator(self.taskset_count, self.tasks_per_taskset, self.interference_factor, self.probability_factor)

    def init_taskset_set(self):
        utilizations = self.utilization_generator.generate_utilizations()
        periods = self.period_generator.generate_periods()
        wcets = self.wcet_calculator.compute_wcets(periods, utilizations)
        interferences = self.interference_generator.generate_interference(wcets)
        deadlines = periods[:]  # TO DO: Implement deadline properly
        return [periods, deadlines, utilizations, wcets, interferences]

    def generate_taskset_set(self):
        periods, deadlines, utilizations, wcets, interferences = self.init_taskset_set()
        taskset_set_generated = []
        for i in range(len(periods)):
            taskset_set_generated.append(Taskset(taskset_number=i, wcet=wcets[i], deadline=deadlines[i], period=periods[i], interference=interferences[i], utilization=utilizations[i]))
        res = TasksetSet(taskset_set_number=self.taskset_set_number, wcet=wcets, deadline=deadlines, period=periods, interference=interferences, utilization=utilizations, taskset_list=taskset_set_generated)
        return res
