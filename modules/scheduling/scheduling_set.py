from modules.scheduling.scheduling import Scheduling

class SchedulingSet:
    def __init__(self, scheduling_id, taskset_id, assignment_id, scheduling_algorithms, scheduling_list):
        self.scheduling_id = scheduling_id
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_algorithms = scheduling_algorithms
        self.scheduling_list = scheduling_list

    def __repr__(self):
        return ("SchedulingSet("
                f"scheduling_id={self.scheduling_id}, "
                f"taskset_id={self.taskset_id}, "
                f"assignment_id={self.assignment_id}, "
                f"scheduling_algorithms={self.scheduling_algorithms}, "
                f"scheduling_list={self.scheduling_list}, "
                ")"
        )

    def __len__(self):
        return len(self.schedule_list)

    def __iter__(self):
        return iter(self.schedule_list)

    def __next__(self):
        return next(self.schedule_list)

    def __getitem__(self, i):
        return self.schedule_list[i]

    def __str__(self):
        res = (f"Scheduling id: {self.scheduling_id}\n"
               f"Taskset ID: {self.taskset_id}\n"
               f"Assignment ID: {self.assignment_id}\n"
               f"Scheduling Algorithms: {self.scheduling_algorithms}\n"
               f"Scheduling List: {self.scheduling_list}\n"
               )

        return res