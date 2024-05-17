import numpy
from modules.experience_generation.task_model.utilization_generation import UtilizationGeneration
from modules.experience_generation.task_model.period_generation import PeriodGeneration
from modules.experience_generation.task_model.wcet_calculation import WCETCalculation
from modules.experience_generation.task_model.interference_generation import InterferenceGeneration
from modules.experience_generation.taskset_set import TasksetSet
from modules.taskset import Taskset
from modules.experience_generation.task_model.matrix_m import MatrixM


class TasksetSetGeneration:
    def __init__(self, _taskset_set_number, _number_of_taskset, _period_min, _period_max, _granularity, 
                _number_of_task_in_taskset, _interference_factor, _probability_factor, _method_of_period_generation, 
                _max_utilization):
        self.taskset_set_number = _taskset_set_number
        self.number_of_taskset = _number_of_taskset
        self.period_min = _period_min
        self.period_max = _period_max
        self.granularity = _granularity
        self.number_of_task_in_taskset = _number_of_task_in_taskset
        self.interference_factor = _interference_factor
        self.probability_factor = _probability_factor
        self.method_of_period_generation = _method_of_period_generation
        self.max_utilization = _max_utilization

        self.matrixM_obj = MatrixM(hyperperiod_limit=100000, max_prime=20, generation_limit_exponent=2)
        self.matrixM = self.matrixM_obj.matrix

        self.utilization_generation = UtilizationGeneration(self.number_of_taskset, self.number_of_task_in_taskset, self.max_utilization)
        self.period_generation = PeriodGeneration(self.number_of_taskset, self.number_of_task_in_taskset, self.period_min, self.period_max, self.granularity, self.method_of_period_generation, self.matrixM)
        self.wcet_calculation = WCETCalculation(self.number_of_taskset, self.number_of_task_in_taskset)
        self.interference_generation = InterferenceGeneration(self.number_of_taskset, self.number_of_task_in_taskset, self.interference_factor, self.probability_factor)

    def init_taskset_set(self):
        utilizations = self.utilization_generation.StaffordRandFixedSum()
        periods = self.period_generation.gen_periods()
        wcets = self.wcet_calculation.calculate_wcets(periods, utilizations)
        interferences = self.interference_generation.gen_interference(wcets)
        deadline = periods[:]  # TO DO: Implement deadline properly
        return [periods, deadline, utilizations, wcets, interferences]

    def generate_taskset_set(self):
        period, deadline, utilization, wcet, interference = self.init_taskset_set()
        taskset_set_generated = []
        for i in range(len(period)):
            taskset_set_generated.append(Taskset(_taskset_number=i, _wcet=wcet[i], _deadline=deadline[i], _period=period[i], _interference=interference[i], _utilization=utilization[i]))
        res = TasksetSet(_taskset_set_number=self.taskset_set_number, _wcet=wcet, _deadline=deadline, _period=period, _interference=interference, _utilization=utilization, _taskset_list=taskset_set_generated)
        return res
