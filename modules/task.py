import math
from .job import Job
class Task:
    def __init__(self, _task_number, _wcet, _deadline, _period, _interference, _utilization):
        self.task_number = _task_number
        self.wcet = _wcet
        self.deadline = _deadline
        self.period = _period
        self.interference = _interference
        self.utilization = _utilization
        self.job_list = []

    def __repr__(self):
        return ("Task("
            f"_task_number={self.task_number} ,"
            f"_wcet={self.wcet}, "
            f"_deadline={self.deadline}, "
            f"_period={self.period}, "
            f"_interference={self.interference}, "
            f"_utilization={self.utilization}"
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
            f"Utilization: {self.utilization}\n"
            f"Jobs of the Task: "
            )
        for elem in self.job_list:
            res = res + "\n" + str(elem)
        if len(self.job_list) == 0:
            res = res + "[]"
        return res

    def create_jobs(self, start_time, finish_time): #task est statique, job dynamique, donc pas dans l'init, on les crée a part qu'a l'utilisation
        self.job_list = []
        number_of_jobs = math.ceil((finish_time-start_time)/self.period)
        number_of_jobs_already_created = math.ceil(start_time/self.period)
        for i in range(number_of_jobs):            
            new_job = Job(_task_number=self.task_number, _job_identifier=i+number_of_jobs_already_created,_job_number=i, _execution_time=self.wcet, _relative_deadline=self.deadline, _period=self.period, _interference=self.interference)
            self.job_list.append(new_job)


    
