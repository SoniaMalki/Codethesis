from .taskset import Taskset

class TasksetSet:
    def __init__(self, _taskset_set_number, _wcet, _deadline, _period , _interference, _utilization, _taskset_list):
        #Task(C,D,T,I)
        self.taskset_set_number = _taskset_set_number
        self.wcet = _wcet
        self.deadline = _deadline
        self.period = _period
        self.interference = _interference
        self.utilization = _utilization
        self.taskset_list = _taskset_list

    def __repr__(self):
        return ("TasksetSet("
            f"_taskset_set_number={self.taskset_set_number}, "
            f"_wcet={self.wcet}, "
            f"_deadline={self.deadline}, "
            f"_period={self.period}, "
            f"_interference={self.interference}, "
            f"_utilization={self.utilization}, "
            f"_taskset_list={repr(self.taskset_list)} "
            ")"
        )

    def __len__(self):
        return len(self.taskset_list)

    def __iter__(self):
        return iter(self.taskset_list)

    def __next__(self):
        return next(self.taskset_list)

    def __getitem__(self, i):
        return self.taskset_list[i]

    def __str__(self):
        res= (f"TasksetSet number: {self.taskset_set_number}\n"
            f"With WCET: {self.wcet}\n"
            f"Deadline: {self.deadline}\n"
            f"Period: {self.period}\n"
            f"Interference: {self.interference}\n"
            f"Utilization: {self.utilization}\n"
            f"Taskset in the set:" 
            )
        for elem in self.taskset_list:
            res = res + "\n" + str(elem)
        if len(self.taskset_list) == 0:
            res = res + "[]\n"
        return res





