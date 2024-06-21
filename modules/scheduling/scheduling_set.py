from modules.scheduling.schedule import Schedule

class SchedulingSet:
    def __init__(self, scheduling_id, taskset_id, assignment_id, scheduling_algorithm, schedule_list):
        self.scheduling_id = scheduling_id
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_algorithm = scheduling_algorithm
        self.schedule_list = schedule_list

    def __repr__(self):
        return ("SchedulingSet("
                f"scheduling_id={self.scheduling_id}, "
                f"taskset_id={self.taskset_id}, "
                f"assignment_id={self.assignment_id}, "
                f"scheduling_algorithm={self.scheduling_algorithm}, "
                f"schedule_list={self.schedule_list}, "
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
               f"Scheduling Algorithm: {self.scheduling_algorithm}\n"
               f"Schedule List: {self.schedule_list}\n"
               )

        return res