from modules.taskset.task import Task


class TasksetSet:
    def __init__(self, taskset_id, wcet, deadline, period, interference, single_interference, utilization, taskset_list):
        self.taskset_id = taskset_id
        self.wcet = wcet
        self.deadline = deadline
        self.period = period
        self.interference = interference
        self.single_interference = single_interference
        self.utilization = utilization
        self.taskset_list = taskset_list
        self.taskset_repetition = None
        self.tasks_per_taskset = None
        self.interference_factor = None
        self.probability_factor = None
        self.max_utilization = None
        self.deadline_option = None
        self.max_hyperperiod = None
        self.max_prime = None
        self.gen_limit_exponent = None

    def __repr__(self):
        return (
            f"TasksetSet(taskset_id={self.taskset_id}, taskset_list={len(self.taskset_list)}, "
            f"wcet={self.wcet}, deadline={self.deadline}, period={self.period}, "
            f"interference={self.interference}, single_interference={self.single_interference}, "
            f"utilization={self.utilization})"
        )

    def __str__(self):
        taskset_str = "\n".join(repr(taskset) for taskset in self.taskset_list)
        return (
            f"TasksetSet ID: {self.taskset_id}\n"
            f"WCET: {self.wcet}\n"
            f"Deadline: {self.deadline}\n"
            f"Period: {self.period}\n"
            f"Interference: {self.interference}\n"
            f"Single Interference: {self.single_interference}\n"
            f"Utilization: {self.utilization}\n"
            f"Tasksets:\n{taskset_str}"
        )

    def __len__(self):
        return len(self.taskset_list)

    def __iter__(self):
        return iter(self.taskset_list)

    def __next__(self):
        return next(self.taskset_list)

    def __getitem__(self, i):
        return self.taskset_list[i]

    def __eq__(self, other):
        if not isinstance(other, TasksetSet):
            return NotImplemented
        return (self.taskset_id == other.taskset_id and
                self.wcet == other.wcet and
                self.deadline == other.deadline and
                self.period == other.period and
                self.interference == other.interference and
                self.single_interference == other.single_interference and
                self.utilization == other.utilization and
                self.taskset_list == other.taskset_list)

    def add_generation_parameters(self, taskset_repetition, tasks_per_taskset, interference_factor, probability_factor, max_utilization, deadline_option, max_hyperperiod, max_prime, gen_limit_exponent):
        self.taskset_repetition = taskset_repetition
        self.tasks_per_taskset = tasks_per_taskset
        self.interference_factor = interference_factor
        self.probability_factor = probability_factor
        self.max_utilization = max_utilization
        self.deadline_option = deadline_option
        self.max_hyperperiod = max_hyperperiod
        self.max_prime = max_prime
        self.gen_limit_exponent = gen_limit_exponent
