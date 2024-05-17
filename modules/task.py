import math
from .job import Job

class Task:
    def __init__(self, task_number, wcet, deadline, period, interference, utilization):
        self.task_number = task_number
        self.wcet = wcet
        self.deadline = deadline
        self.period = period
        self.interference = interference
        self.utilization = utilization
        self.job_list = []

    def __repr__(self):
        return ("Task("
                f"task_number={self.task_number}, "
                f"wcet={self.wcet}, "
                f"deadline={self.deadline}, "
                f"period={self.period}, "
                f"interference={self.interference}, "
                f"utilization={self.utilization}"
                ")"
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
        res = (f"Task number: {self.task_number}\n"
               f"WCET: {self.wcet}\n"
               f"Deadline: {self.deadline}\n"
               f"Period: {self.period}\n"
               f"Interference: {self.interference}\n"
               f"Utilization: {self.utilization}\n")
        job_str = "Jobs of the Task: "
        for elem in self.job_list:
            job_str = job_str + "\n" + str(elem)
        if len(self.job_list) == 0:
            job_str = job_str + "[]"
        res = res + job_str
        return res

    def create_jobs(self, start_time, finish_time):
        self.job_list = []
        number_of_jobs = math.ceil((finish_time - start_time) / self.period)
        number_of_jobs_already_created = math.ceil(start_time / self.period)
        for i in range(number_of_jobs):
            new_job = Job(task_number=self.task_number, job_identifier=i + number_of_jobs_already_created, job_number=i, execution_time=self.wcet, relative_deadline=self.deadline, period=self.period, interference=self.interference)
            self.job_list.append(new_job)
