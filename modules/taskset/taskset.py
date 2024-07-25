from .task import Task


class Taskset:
    def __init__(self, taskset_number, wcet, deadline, period, interference, single_interference, utilization, hyperperiod, N, activation, absolute_deadline):
        self.taskset_number = taskset_number
        self.wcet = wcet
        self.deadline = deadline
        self.period = period
        self.interference = interference
        self.single_interference = single_interference
        self.utilization = utilization
        self.hyperperiod = hyperperiod
        self.N = N
        self.activation = activation
        self.absolute_deadline = absolute_deadline

        self.task_list = []
        for i in range(len(self.period)):
            self.task_list.append(Task(task_number=i, wcet=self.wcet[i], deadline=self.deadline[i],
                                       period=self.period[i], interference=self.interference[
                                           i], single_interference=self.single_interference[i], utilization=self.utilization[i],
                                       absolute_deadline=self.absolute_deadline[i]))

    def __repr__(self):
        return (
            f"Taskset(taskset_number={self.taskset_number}, task_list={len(self.task_list)}, "
            f"wcet={self.wcet}, deadline={self.deadline}, period={self.period}, "
            f"interference={self.interference}, single_interference={self.single_interference}, "
            f"utilization={self.utilization}, hyperperiod={self.hyperperiod}, "
            f"N={self.N}, activation={self.activation}, absolute_deadline={self.absolute_deadline})"
        )

    def __str__(self):
        task_str = "\n".join(repr(task) for task in self.task_list)
        return (
            f"Taskset Number: {self.taskset_number}\n"
            f"WCET: {self.wcet}\n"
            f"Deadline: {self.deadline}\n"
            f"Period: {self.period}\n"
            f"Interference: {self.interference}\n"
            f"Single Interference: {self.single_interference}\n"
            f"Utilization: {self.utilization}\n"
            f"Hyperperiod: {self.hyperperiod}\n"
            f"N: {self.N}\n"
            f"Activation: {self.activation}\n"
            f"Absolute Deadline: {self.absolute_deadline}\n"
            f"Tasks:\n{task_str}"
        )

    def __len__(self):
        return len(self.task_list)

    def __iter__(self):
        return iter(self.task_list)

    def __next__(self):
        return next(self.task_list)

    def __getitem__(self, i):
        return self.task_list[i]

    def __eq__(self, other):
        if not isinstance(other, Taskset):
            return NotImplemented
        return (self.taskset_number == other.taskset_number and
                self.wcet == other.wcet and
                self.deadline == other.deadline and
                self.period == other.period and
                self.interference == other.interference and
                self.single_interference == other.single_interference and
                self.utilization == other.utilization and
                self.hyperperiod == other.hyperperiod and
                self.N == other.N and
                self.activation == other.activation and
                self.absolute_deadline == other.absolute_deadline and
                self.task_list == other.task_list)
