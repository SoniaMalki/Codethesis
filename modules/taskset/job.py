class Job:
    def __init__(self, task_number, job_identifier, wcet, relative_deadline):
        # To identify job
        self.task_number = task_number
        self.job_identifier = job_identifier
        # Fixed attributes
        self.wcet = wcet
        self.relative_deadline = relative_deadline

        # Changing attributes
        self.execution_time = 0  
        self.completed = False

    def __repr__(self):
        return (
            "Job("
            f"task_number={self.task_number}, "
            f"job_identifier={self.job_identifier}, "
            f"wcet={self.wcet}, "
            f"relative_deadline={self.relative_deadline}, "
            f"execution_time={self.execution_time}, "
            f"completed={self.completed}"
            ")"
        )

    def __str__(self):
        res = (f"Job identifier: {self.job_identifier}\n"
               f"WCET: {self.execution_time}\n"
               f"Relative Deadline: {self.relative_deadline}\n"
               f"Completed: {self.completed}\n"
               f"Remaining Execution Time: {self.execution_time}")
        return res

    def execute(self, time_slice):
        if self.execution_time < self.wcet:
            self.execution_time += time_slice
            if self.execution_time >= self.wcet:
                self.is_finished = True



