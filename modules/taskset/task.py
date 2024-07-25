import math
import time
from modules.taskset.job import Job


class Task:
    def __init__(self, task_number, wcet, deadline, period, interference, single_interference, utilization, absolute_deadline):
        self.task_number = task_number
        self.wcet = wcet
        self.deadline = deadline
        self.period = period
        self.interference = interference
        self.single_interference = single_interference
        self.utilization = utilization
        self.absolute_deadline = absolute_deadline

        self.job_list = []

    def __repr__(self):
        return (
            f"Task(task_number={self.task_number}, wcet={self.wcet}, deadline={self.deadline}, "
            f"period={self.period}, interference={self.interference}, single_interference={self.single_interference}, "
            f"utilization={self.utilization}, absolute_deadline={self.absolute_deadline})"
        )

    def __len__(self):
        return len(self.job_list)

    def __iter__(self):
        return iter(self.job_list)

    def __next__(self):
        return next(self.job_list)

    def __getitem__(self, i):
        return self.job_list[i]

    def __str__(self):
        job_str = "\n".join(repr(job) for job in self.job_list)
        return (
            f"Task Number: {self.task_number}\n"
            f"WCET: {self.wcet}\n"
            f"Deadline: {self.deadline}\n"
            f"Period: {self.period}\n"
            f"Interference: {self.interference}\n"
            f"Single Interference: {self.single_interference}\n"
            f"Utilization: {self.utilization}\n"
            f"Absolute Deadline: {self.absolute_deadline}\n"
            f"Jobs: \n{job_str}"
        )

    def create_jobs(self, start_time, end_time):
        self.job_list = []

        first_arrival_time = self.period * \
            math.ceil((start_time-1) / self.period) + 1
        number_of_jobs = math.ceil(
            (end_time - first_arrival_time) / self.period) + 1
        first_job_identifier = math.ceil(start_time-1 / self.period)

        for i in range(number_of_jobs):
            job_identifier = first_job_identifier + i
            arrival_time = first_arrival_time + i * self.period
            relative_deadline = arrival_time + self.deadline

            job = Job(
                task_number=self.task_number,
                job_identifier=job_identifier,
                wcet=self.wcet,
                absolute_deadline=self.deadline,
                relative_deadline=relative_deadline,
                arrival_time=arrival_time,
                interference_factor=self.single_interference
            )
            self.job_list.append(job)

    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (self.task_number == other.task_number and
                self.wcet == other.wcet and
                self.deadline == other.deadline and
                self.period == other.period and
                self.interference == other.interference and
                self.single_interference == other.single_interference and
                self.utilization == other.utilization and
                self.absolute_deadline == other.absolute_deadline and
                self.job_list == other.job_list)
