import numpy as np
from modules.scheduling.scheduling import Scheduling


class SchedulingSet:
    def __init__(self, scheduling_id, taskset_id, assignment_id, scheduling_algorithm, scheduling_options, scheduling_list):
        self.scheduling_id = scheduling_id
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_algorithm = scheduling_algorithm
        self.scheduling_options = scheduling_options
        self.scheduling_list = scheduling_list

        self.mean_success = self.calculate_mean_success()
        self.mean_computation_time = self.calculate_mean_computation_time()
        self.mean_theoritical_utilization = self.calculate_mean_theoritical_utilization()
        self.mean_actual_utilization = self.calculate_mean_actual_utilization()
        self.mean_overutilization = self.calculate_mean_overutilization()

    def __repr__(self):
        return (
            f"SchedulingSet(scheduling_id={self.scheduling_id}, taskset_id={self.taskset_id}, "
            f"assignment_id={self.assignment_id}, scheduling_algorithm={self.scheduling_algorithm}, "
            f"scheduling_options={self.scheduling_options}, scheduling_list={len(self.scheduling_list)})"
        )

    def __str__(self):
        scheduling_str = "\n".join(repr(scheduling)
                                   for scheduling in self.scheduling_list)
        return (
            f"Scheduling ID: {self.scheduling_id}\n"
            f"Taskset ID: {self.taskset_id}\n"
            f"Assignment ID: {self.assignment_id}\n"
            f"Algorithm: {self.scheduling_algorithm}\n"
            f"Options: {self.scheduling_options}\n"
            f"Schedulings:\n{scheduling_str}"
        )

    def __len__(self):
        return len(self.scheduling_list)

    def __iter__(self):
        return iter(self.scheduling_list)

    def __next__(self):
        return next(self.scheduling_list)

    def __getitem__(self, i):
        return self.scheduling_list[i]

    def __eq__(self, other):
        if not isinstance(other, SchedulingSet):
            return NotImplemented
        return self.scheduling_list == other.scheduling_list

    def calculate_mean_success(self):
        return np.mean([scheduling.success for scheduling in self.scheduling_list])

    def calculate_mean_computation_time(self):
        return np.mean([scheduling.computation_time for scheduling in self.scheduling_list])

    def calculate_mean_actual_utilization(self):
        return np.mean([scheduling.actual_utilization for scheduling in self.scheduling_list])

    def calculate_mean_theoritical_utilization(self):
        return np.mean([scheduling.theoritical_utilization for scheduling in self.scheduling_list])

    def calculate_mean_overutilization(self):
        return (
            (
                self.mean_actual_utilization
                - self.mean_theoritical_utilization
            )
            / self.mean_theoritical_utilization
        ) * 100
