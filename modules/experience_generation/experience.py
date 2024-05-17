class Experience:       
    def __init__(self, number_of_cores, taskset_count, list_of_tasks_per_taskset, 
                 list_of_interference_factors, list_of_probability_factors, 
                 min_period, max_period, granularity, list_of_period_generation_methods, 
                 list_of_sorting_criteria, list_of_max_utilization, 
                 experience_length, taskset_set_list):
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
        self.list_of_max_utilization = list_of_max_utilization

        # Other parameters
        self.experience_length = experience_length
        self.taskset_set_list = taskset_set_list

    def __repr__(self):
        return ("Experience("
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
                f"list_of_max_utilization={self.list_of_max_utilization}, "
                f"experience_length={self.experience_length}, "
                f"taskset_set_list={repr(self.taskset_set_list)}"
                ")"
        )

    def __len__(self):
        return len(self.taskset_set_list)

    def __iter__(self):
        return iter(self.taskset_set_list)

    def __next__(self):
        return next(self.taskset_set_list)

    def __getitem__(self, i):
        return self.taskset_set_list[i]

    def __str__(self):
        res = (f"Experience with parameters:\n"
               f"Number of cores: {self.number_of_cores}\n"
               f"Number of taskset: {self.taskset_count}\n"
               f"Minimum/Maximum values for periods: {self.min_period}/{self.max_period}\n"
               f"Granularity used for period generation: {self.granularity}\n"
               f"List of sorting criteria: {self.list_of_sorting_criteria}\n"
               f"List of number of tasks in taskset: {self.list_of_tasks_per_taskset}\n"
               f"List of interference factors for generation of interference: {self.list_of_interference_factors}\n"
               f"List of probability of two tasks interfering with each other: {self.list_of_probability_factors}\n"
               f"List of methods used for period generation: {self.list_of_period_generation_methods}\n"
               f"List of maximum utilization used for WCET generation: {self.list_of_max_utilization}\n"
               f"Length of the experience (how many sets of tasksets created?): {self.experience_length}\n"
               f"List of generated sets of tasksets:")
        for elem in self.taskset_set_list:
            res += "\n" + str(elem)
        if len(self.taskset_set_list) == 0:
            res += "[]"
        return res
