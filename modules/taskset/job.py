import time

class Job:
    def __init__(self, task_number, job_identifier, job_number, execution_time, relative_deadline, period, interference):
        # To identify job
        self.task_number = task_number
        self.job_identifier = job_identifier
        self.job_number = job_number
        # Fixed attributes
        self.execution_time = execution_time
        self.relative_deadline = relative_deadline
        self.period = period
        self.interference = interference

        self.activation_time = self.job_identifier * self.period
        self.absolute_deadline = self.activation_time + self.relative_deadline

        # Changing attributes
        self.starting_time = None
        self.finishing_time = None
        self.status = "Not ready"  # Can be "Not ready" "Ready" "Blocked" "Preempted" "Finished" "Executing"
        self.remaining_execution_time = self.execution_time

    def __repr__(self):
        return ("Job("
                f"task_number={self.task_number}, " 
                f"job_identifier={self.job_identifier}, "
                f"job_number={self.job_number}, "
                f"execution_time={self.execution_time}, "
                f"relative_deadline={self.relative_deadline}, "
                f"period={self.period}, "
                f"interference={self.interference}, "
                f"remaining_execution_time={self.remaining_execution_time}"
                ")"
        )

    def __str__(self):
        res = (f"Job identifier: {self.job_identifier}\n"
               f"WCET: {self.execution_time}\n"
               f"Relative deadline: {self.relative_deadline}\n"
               f"Period: {self.period}\n"
               f"Interference: {self.interference}\n"
               f"Activation time: {self.activation_time}\n"
               f"Absolute deadline: {self.absolute_deadline}\n"
               f"Starting time: {self.starting_time}\n"
               f"Finishing time: {self.finishing_time}\n"
               f"Status: {self.status}\n"
               f"Remaining Execution Time: {self.remaining_execution_time}")
        return res

    def execute(self, current_time):
        if self.remaining_execution_time > 0 and self.status == "Ready":
            if self.starting_time is None:
                self.starting_time = current_time
            self.remaining_execution_time -= 1

    def update_status(self, current_time):
        # TO DO: Add conditions for blocked, preempted...
        if self.remaining_execution_time == 0:
            if self.status != "Finished":
                self.finishing_time = current_time
            self.status = "Finished"
        elif self.remaining_execution_time > 0 and self.absolute_deadline <= current_time:
            self.status = "Error"
        elif self.activation_time > current_time:
            self.status = "Not Ready"
        elif self.activation_time <= current_time and self.status != "Finished":
            self.status = "Ready"
        else:
            print("\n\n\ncurrent_time", current_time)
            print("status", self.status)
            print("remaining_execution_time", self.remaining_execution_time)
            print("activation_time", self.activation_time)
            print("absolute_deadline", self.absolute_deadline)
            print(self.__str__())
            raise Exception("Status Ambiguous")