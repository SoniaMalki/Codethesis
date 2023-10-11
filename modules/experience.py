class Experience:       
    def __init__(self, _number_of_cores, _number_of_taskset, _period_min, _period_max, _granularity, _list_of_sorting_criterion,
                        _list_of_number_of_task_in_taskset, _list_of_interference_factor, _list_of_probability_factor, _list_of_method_of_period_generation, _list_of_max_utilization, 
                        _experience_lenght, _taskset_set_list):
        #parameters that stay the same
        self.number_of_cores= _number_of_cores
        self.number_of_taskset = _number_of_taskset
        self.period_min = _period_min
        self.period_max = _period_max
        self.granularity = _granularity
        self.list_of_sorting_criterion = _list_of_sorting_criterion

        #parameters that varies
        self.list_of_number_of_task_in_taskset = _list_of_number_of_task_in_taskset
        self.list_of_interference_factor = _list_of_interference_factor
        self.list_of_probability_factor = _list_of_probability_factor
        self.list_of_max_utilization = _list_of_max_utilization
        self.list_of_method_of_period_generation = _list_of_method_of_period_generation
        self.experience_lenght = _experience_lenght
        self.taskset_set_list = _taskset_set_list

    def __repr__(self):
        return ("Experience("
            f"_number_of_cores={self.number_of_cores}, "
            f"_number_of_taskset={self.number_of_taskset}, "
            f"_period_min={self.period_min}, "
            f"_period_max={self.period_max}, "
            f"_granularity={self.granularity}, "
            f"_list_of_sorting_criterion={self.list_of_sorting_criterion}, "
            f"_list_of_number_of_task_in_taskset={self.list_of_number_of_task_in_taskset}, "
            f"_list_of_interference_factor={self.list_of_interference_factor}, "
            f"_list_of_probability_factor={self.list_of_probability_factor}, "
            f"_list_of_method_of_period_generation={self.list_of_method_of_period_generation}, "
            f"_list_of_max_utilization={self.list_of_max_utilization}, "
            f"_experience_lenght={self.experience_lenght}, "
            f"_taskset_set_list={repr(self.taskset_set_list)}"
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
        res= (f"Experience with parameters:\n"
            f"Number of cores: {self.number_of_cores}\n"
            f"Number of taskset: {self.number_of_taskset}\n"
            f"Minimum/Maximum values for periods: {self.period_min}/{self.period_max}\n"
            f"Granularity used for period generation: {self.granularity}\n"
            f"List of sorting criterion: {self.list_of_sorting_criterion}\n"
            f"List of number of tasks in taskset: {self.list_of_number_of_task_in_taskset}\n"
            f"List of interference factor for generation of interference: {self.list_of_interference_factor}\n"
            f"List of probability of two tasks interfering with each other: {self.list_of_probability_factor}\n"
            f"List of methods used for period generation: {self.list_of_method_of_period_generation}\n"
            f"List of maximum utilization used for wcet generation: {self.list_of_max_utilization}\n"
            f"Lenght of the experience (how much set of taskset created?): {self.experience_lenght}\n"
            f"List of generated set of taskset:"
            )
        for elem in self.taskset_set_list:
            res = res + "\n" + str(elem)
        if len(self.taskset_set_list) == 0:
            res = res + "[]"
        return res



    # def __str__(self):
    #     res = ""
    #     res += (
    #         f"Experience n{self.experience_number} generated with parameters:\n"
    #         f"Number of taskset generated: {self.number_of_taskset}\n"
    #         f"How many tasks per taskset: {self.number_of_tasks}\n"
    #         f"Maximum utilization factor per taskset: {self.u_max}\n"
    #         f"Minimum period for the tasks, maximum period for the tasks: min={self.period_min}/max={self.period_max}\n"
    #         f"Interference factor used for interference generation: {self.list_of_interference_factor}\n"
    #         f"Probability factor of two tasks generating interference for interference generation: {self.list_of_probability_factor*100} %\n"
    #         f"Method used for generating periods: {self.period_generation_method}\n"
    #         f"\nGenerated taskset in the experience \n"
    #         )
    #     # for taskset_set in self.taskset_set_list:
    #     #     res += taskset_set.nice_output()
    #     return res