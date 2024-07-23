from modules.scheduling.scheduling import Scheduling


class SchedulingSet:
    def __init__(self, scheduling_id, taskset_id, assignment_id, scheduling_algorithm, scheduling_options, scheduling_list):
        self.scheduling_id = scheduling_id
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_algorithm = scheduling_algorithm
        self.scheduling_options = scheduling_options
        self.scheduling_list = scheduling_list

    def __repr__(self):
        return ("SchedulingSet("
                f"scheduling_id={self.scheduling_id}, "
                f"taskset_id={self.taskset_id}, "
                f"assignment_id={self.assignment_id}, "
                f"scheduling_algorithms={self.scheduling_algorithm}, "
                f"scheduling_list={self.scheduling_list}, "
                ")"
                )

    def __len__(self):
        return len(self.scheduling_list)

    def __iter__(self):
        return iter(self.scheduling_list)

    def __next__(self):
        return next(self.scheduling_list)

    def __getitem__(self, i):
        return self.scheduling_list[i]

    def __str__(self):
        res = (f"Scheduling id: {self.scheduling_id}\n"
               f"Taskset ID: {self.taskset_id}\n"
               f"Assignment ID: {self.assignment_id}\n"
               f"Scheduling Algorithm: {self.scheduling_algorithm}\n"
               f"Scheduling List: {self.scheduling_list}\n"
               )

        return res

    def __eq__(self, other):
        if not isinstance(other, SchedulingSet):
            return NotImplemented
        return (self.scheduling_list == other.scheduling_list)
