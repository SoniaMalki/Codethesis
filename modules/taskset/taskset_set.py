from modules.taskset.task import Task

class TasksetSet:
    def __init__(self, taskset_id, wcet, deadline, period, interference, utilization, taskset_list):
        self.taskset_id = taskset_id
        self.wcet = wcet
        self.deadline = deadline
        self.period = period
        self.interference = interference
        self.utilization = utilization
        self.taskset_list = taskset_list

    def __repr__(self):
        return ("TasksetSet("
                f"taskset_id={self.taskset_id}, "
                f"wcet={self.wcet}, "
                f"deadline={self.deadline}, "
                f"period={self.period}, "
                f"interference={self.interference}, "
                f"utilization={self.utilization}, "
                f"taskset_list={repr(self.taskset_list)} "
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
        res = (f"TasksetSet id: {self.taskset_id}\n"
               f"With WCET: {self.wcet}\n"
               f"Deadline: {self.deadline}\n"
               f"Period: {self.period}\n"
               f"Interference: {self.interference}\n"
               f"Utilization: {self.utilization}\n"
               f"Taskset in the set:")

        # for elem in self.taskset_list:
        #     res = res + "\n" + str(elem)
        # if len(self.taskset_list) == 0:
        #     res = res + "[]\n"
        return res