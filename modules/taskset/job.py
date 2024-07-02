class Job:
    def __init__(self, task_number, job_identifier, wcet, absolute_deadline, relative_deadline, arrival_time, interference_factor):
        self.task_number = task_number
        self.job_identifier = job_identifier
        self.wcet = wcet
        self.absolute_deadline = absolute_deadline
        self.relative_deadline = relative_deadline
        self.arrival_time = arrival_time
        self.interference_factor = max(interference_factor)
        
        self.remaining_execution_time = self.wcet
        self.completed = False
        self.interference_history = set()  # To keep track of which jobs have interfered

    def __repr__(self):
        return (
            f"Job(task_number={self.task_number}, job_identifier={self.job_identifier}, "
            f"wcet={self.wcet}, relative_deadline={self.relative_deadline}, "
            f"arrival_time={self.arrival_time}, interference_factor={self.interference_factor})"
        )

    def __str__(self):
        return (f"Job identifier: {self.job_identifier}\n"
                f"Arrival time: {self.arrival_time}\n"
                f"WCET: {self.wcet}\n"
                f"Relative Deadline: {self.relative_deadline}\n"
                f"Completed: {self.completed}\n"
                f"Remaining Execution Time: {self.remaining_execution_time}\n"
                f"Interference Received: {self.interference_history}")

    def execute(self):
        if self.remaining_execution_time > 0:
            self.remaining_execution_time -= 1
            if self.remaining_execution_time <= 0:
                self.completed = True

    def apply_interference(self, interfering_job_id, interfering_interference_factor):
        if interfering_job_id not in self.interference_history:
            self.remaining_execution_time += interfering_interference_factor
            self.interference_history.add(interfering_job_id)
