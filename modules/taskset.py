from .task import Task  

class Taskset:
    def __init__(self, _taskset_number, _wcet, _deadline , _period, _interference, _utilization):
        self.taskset_number = _taskset_number
        self.wcet = _wcet
        self.deadline = _deadline
        self.period = _period
        self.interference = _interference
        self.utilization = _utilization
        
        self.task_list = []
        for i in range(len(self.period)):
            self.task_list.append(Task(_task_number=i, _wcet=self.wcet[i], _deadline=self.deadline[i], 
                                _period=self.period[i], _interference=self.interference[i], _utilization=self.utilization[i]
                                ))
    def __repr__(self):
        return ("Taskset("
            f"_taskset_number={self.taskset_number}, "
            f"_wcet={self.wcet}, "
            f"_deadline={self.deadline}, "
            f"_period={self.period}, "
            f"_interference={self.interference}, "
            f"_utilization={self.utilization}"
            ")"
        )

    def __len__(self):
        return len(self.task_list)

    def __iter__(self):
        return iter(self.task_list)

    def __next__(self):
        return next(self.task_list)

    def __getitem__(self, i):
         return self.task_list[i]

    def __str__(self):
        res = (f"Taskset number: {self.taskset_number}\n"
            f"WCET: {self.wcet}\n"
            f"Deadline: {self.deadline}\n"
            f"Period: {self.period}\n"
            f"Interference: {self.interference}\n"
            f"Utilization: {self.utilization}\n"
            )
        task_str = "Task in the taskset:"
        for elem in self.task_list:
            task_str = task_str + "\n" + str(elem)
        if len(self.task_list) == 0:
            task_str = task_str + "[]"
        #res = res + task_str
        return res


