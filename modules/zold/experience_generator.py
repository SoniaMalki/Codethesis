from modules.experience_generation.experience import Experience
from modules.experience_generation.taskset_set_generator import TasksetSetGenerator
import time

class ExperienceGenerator:
    def __init__(self, number_of_cores, taskset_count, list_of_tasks_per_taskset, 
                 list_of_interference_factors, list_of_probability_factors, 
                 min_period, max_period, granularity, list_of_period_generation_methods, 
                 random_generation, list_of_sorting_criteria, list_of_max_utilization):
        # Parameters that stay the same
        self.number_of_cores = number_of_cores
        self.taskset_count = taskset_count
        self.min_period = min_period
        self.max_period = max_period
        self.granularity = granularity
        self.list_of_sorting_criteria = list_of_sorting_criteria

        # Parameters that vary
        self.list_of_tasks_per_taskset = list_of_tasks_per_taskset
        self.list_of_interference_factors = list_of_interference_factors
        self.list_of_probability_factors = list_of_probability_factors
        self.list_of_period_generation_methods = list_of_period_generation_methods
        self.random_generation = random_generation

        # Parameters that are generated 
        self.list_of_max_utilization = list_of_max_utilization
        if len(self.list_of_max_utilization) == 0:
            self.u_fix = self.number_of_cores - 1
            while self.u_fix > 0.1:
                self.list_of_max_utilization.append(self.u_fix)
                self.u_fix -= 0.2

    def __repr__(self):
        return (f"ExperienceGenerator("
                f"number_of_cores={self.number_of_cores}, "
                f"taskset_count={self.taskset_count}, "
                f"min_period={self.min_period}, "
                f"max_period={self.max_period}, "
                f"granularity={self.granularity}, "
                f"list_of_sorting_criteria={self.list_of_sorting_criteria}, "
                f"list_of_tasks_per_taskset={self.list_of_tasks_per_taskset}, "
                f"list_of_interference_factors={self.list_of_interference_factors}, "
                f"list_of_probability_factors={self.list_of_probability_factors}, "
                f"list_of_period_generation_methods={self.list_of_period_generation_methods}, "
                f"random_generation={self.random_generation}, "
                f"list_of_max_utilization={self.list_of_max_utilization}"
                ")")

    def generate_experience(self, output_bool=False):
        taskset_set_number = 0
        experience_length = int(len(self.list_of_tasks_per_taskset) * len(self.list_of_probability_factors) * len(self.list_of_interference_factors) * len(self.list_of_period_generation_methods) * len(self.list_of_max_utilization))
        experience_generated = []

        for tasks_per_taskset in self.list_of_tasks_per_taskset:
            for interference_factor in self.list_of_interference_factors:
                for probability_factor in self.list_of_probability_factors:
                    for period_generation_method in self.list_of_period_generation_methods:
                        for max_utilization in self.list_of_max_utilization:
                            if output_bool:
                                print(f"Generating taskset set {taskset_set_number + 1} of {experience_length}")
                            experience_generated.append(TasksetSetGenerator(taskset_set_number=taskset_set_number, taskset_count=self.taskset_count, 
                                                                            min_period=self.min_period, max_period=self.max_period, granularity=self.granularity, 
                                                                            tasks_per_taskset=tasks_per_taskset, interference_factor=interference_factor, 
                                                                            probability_factor=probability_factor, period_generation_method=period_generation_method, 
                                                                            max_utilization=max_utilization).generate_taskset_set())
                            taskset_set_number += 1
        
        res = Experience(number_of_cores=self.number_of_cores, taskset_count=self.taskset_count, min_period=self.min_period, max_period=self.max_period, 
                         granularity=self.granularity, list_of_sorting_criteria=self.list_of_sorting_criteria, list_of_tasks_per_taskset=self.list_of_tasks_per_taskset, 
                         list_of_interference_factors=self.list_of_interference_factors, list_of_probability_factors=self.list_of_probability_factors, 
                         list_of_period_generation_methods=self.list_of_period_generation_methods, list_of_max_utilization=self.list_of_max_utilization, 
                         experience_length=experience_length, taskset_set_list=experience_generated)

        return res
