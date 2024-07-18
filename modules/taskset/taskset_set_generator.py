import math
import time
import numpy
from math import gcd

from sympy import hyper
from modules.taskset.task_parameters_generator.deadline_generator import DeadlineGenerator
from modules.taskset.task_parameters_generator.utilization_generator import UtilizationGenerator
from modules.taskset.task_parameters_generator.period_generator import PeriodGenerator
from modules.taskset.task_parameters_generator.wcet_calculator import WCETCalculator
from modules.taskset.task_parameters_generator.interference_generator import InterferenceGenerator
from modules.taskset.task_parameters_generator.prime_matrix_generator import PrimeMatrixGenerator
from modules.taskset.taskset_set import TasksetSet
from modules.taskset.taskset import Taskset
from modules.taskset.task import Task


class TasksetSetGenerator:
    def __init__(self, taskset_id, taskset_repetition, tasks_per_taskset, list_of_interference_factors, list_of_probability_factors, list_of_max_utilization, taskset_options):

        self.taskset_id = taskset_id
        self.taskset_repetition = taskset_repetition
        self.tasks_per_taskset = tasks_per_taskset
        self.interference_factor = list_of_interference_factors[0]
        self.probability_factor = list_of_probability_factors[0]
        self.max_utilization = list_of_max_utilization[0]
        self.taskset_options = taskset_options
        self.deadline_option = self.taskset_options["deadline_option"]

        self.prime_matrix_generator = PrimeMatrixGenerator(
            max_hyperperiod=100000, max_prime=20, gen_limit_exponent=2)
        self.prime_matrix = self.prime_matrix_generator.prime_matrix

        self.utilization_generator = UtilizationGenerator(
            self.taskset_repetition, self.tasks_per_taskset, self.max_utilization)
        self.period_generator = PeriodGenerator(
            self.taskset_repetition, self.tasks_per_taskset, self.prime_matrix)
        self.wcet_calculator = WCETCalculator(
            self.taskset_repetition, self.tasks_per_taskset)
        self.deadline_generator = DeadlineGenerator()
        self.interference_generator = InterferenceGenerator(
            self.taskset_repetition, self.tasks_per_taskset, self.interference_factor, self.probability_factor)

    @staticmethod
    def calculate_lcm(period):
        lcm = period[0]
        for i in range(1, len(period)):
            lcm = lcm * period[i] // gcd(lcm, period[i])
        return lcm

    @staticmethod
    def generate_hyperperiods(periods):
        hyperperiods = numpy.zeros(len(periods), dtype=int)
        for taskset_index, period in enumerate(periods):
            hyperperiods[taskset_index] = TasksetSetGenerator.calculate_lcm(
                period=period)
        return hyperperiods

    @staticmethod
    def generate_N(periods, hyperperiods):
        N = numpy.zeros((len(periods),), dtype=object)
        for taskset_index, period in enumerate(periods):
            N[taskset_index] = hyperperiods[taskset_index] / period
        return N

    @staticmethod
    def generate_activations(periods, N):
        activations = numpy.empty(len(periods), dtype=object)
        for taskset_index, period in enumerate(periods):
            tasks_activations = []
            # On ajoute 1 à taskset_index pour commencer l'indexation à 1
            for task_index in range(1, len(period)+1):
                # On décale l'intervalle de 1 pour commencer à 1
                temp = list(
                    range(1, int(N[taskset_index][task_index - 1]) + 1))
                tasks_activations.append(temp)
            activations[taskset_index] = tasks_activations
        return activations

    @staticmethod
    def generate_absolute_deadline(periods, deadlines, activations):
        absolute_deadlines = [None] * len(periods)
        for taskset_index, period in enumerate(periods):
            tasks_absolute_deadline = []
            for task_index in range(len(period)):
                temp = {}
                for a in activations[taskset_index][task_index]:
                    temp[a] = ((a - 1) * periods[taskset_index][task_index] +
                               deadlines[taskset_index][task_index] + 1)
                tasks_absolute_deadline.append(temp)
            absolute_deadlines[taskset_index] = tasks_absolute_deadline
        return absolute_deadlines

    def init_taskset_set(self):
        utilizations = self.utilization_generator.generate_utilizations()
        periods = self.period_generator.generate_periods()
        wcets = self.wcet_calculator.compute_wcets(periods, utilizations)
        interferences = self.interference_generator.generate_interference(
            wcets)
        deadlines = self.deadline_generator.generate_deadlines(
            periods=periods, wcets=wcets, deadline_option=self.deadline_option)
        hyperperiods = TasksetSetGenerator.generate_hyperperiods(
            periods=periods)
        N = TasksetSetGenerator.generate_N(
            periods=periods, hyperperiods=hyperperiods)
        activations = TasksetSetGenerator.generate_activations(
            periods=periods, N=N)
        absolute_deadlines = TasksetSetGenerator.generate_absolute_deadline(
            periods=periods, deadlines=deadlines, activations=activations)
        return [periods, deadlines, utilizations, wcets, interferences, hyperperiods, N, activations, absolute_deadlines]

    def generate_taskset_set(self):
        periods, deadlines, utilizations, wcets, interferences, hyperperiods, N, activations, absolute_deadlines = self.init_taskset_set()
        taskset_set_generated = []
        for i in range(len(periods)):
            taskset_set_generated.append(Taskset(taskset_number=i, wcet=wcets[i], deadline=deadlines[i], period=periods[i], interference=interferences[
                                         i], utilization=utilizations[i], hyperperiod=hyperperiods[i], N=N[i], activation=activations[i], absolute_deadline=absolute_deadlines[i]))
        res = TasksetSet(taskset_id=self.taskset_id, wcet=wcets, deadline=deadlines, period=periods,
                         interference=interferences, utilization=utilizations, taskset_list=taskset_set_generated)
        return res
