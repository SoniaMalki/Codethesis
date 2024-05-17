from .task import Task  

class Taskset:
    def __init__(self, taskset_number, wcet, deadline, period, interference, utilization):
        self.taskset_number = taskset_number
        self.wcet = wcet
        self.deadline = deadline
        self.period = period
        self.interference = interference
        self.utilization = utilization
        
        self.task_list = []
        for i in range(len(self.period)):
            self.task_list.append(Task(task_number=i, wcet=self.wcet[i], deadline=self.deadline[i], 
                                       period=self.period[i], interference=self.interference[i], utilization=self.utilization[i]))

    def __repr__(self):
        return ("Taskset("
                f"taskset_number={self.taskset_number}, "
                f"wcet={self.wcet}, "
                f"deadline={self.deadline}, "
                f"period={self.period}, "
                f"interference={self.interference}, "
                f"utilization={self.utilization}"
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
               f"Utilization: {self.utilization}\n")
        task_str = "Task in the taskset:"
        for elem in self.task_list:
            task_str = task_str + "\n" + str(elem)
        if len(self.task_list) == 0:
            task_str = task_str + "[]"
        res = res + task_str
        return res
