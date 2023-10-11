import time
class Job:
    #objet dynamique
    def __init__(self, _task_number, _job_identifier ,_job_number, _execution_time, _relative_deadline, _period, _interference):
        #to identify job
        self.task_number = _task_number
        self.job_identifier = _job_identifier
        self.job_number = _job_number
        #fixed attributes
        self.execution_time = _execution_time
        self.relative_deadline = _relative_deadline
        self.period = _period
        self.interference = _interference

        self.activation_time = (self.job_identifier * self.period) 
        self.absolute_deadline = self.activation_time + self.relative_deadline

        #changing attributes
        self.starting_time = None
        self.finishing_time = None
        self.status = "Not ready" #can be "Not ready" "Ready" "Blocked" "Preempted" "Finished" "Executing"
        self.remaining_execution_time = self.execution_time

    def __repr__(self):
        return ("Job("
            f"_task_number={self.task_number}, " 
            f"_job_identifier={self.job_identifier}, "
            f"_job_number={self.job_number}, "
            f"_execution_time={self.execution_time}, "
            f"_relative_deadline={self.relative_deadline}, "
            f"_period={self.period}, "
            f"_interference={self.interference}, "
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
            f"Remaning Execution Time: {self.remaining_execution_time}"
            )

        return res


    def execute(self, current_time):
        if self.remaining_execution_time > 0 and self.status == "Ready":
            if self.starting_time == None:
                self.starting_time = current_time
            # if self.job_identifier == 18 and current_time > 126:
            #     print(self.remaining_execution_time, self.task_number, self.job_identifier, current_time)
            #     time.sleep(2)
            self.remaining_execution_time -=1

    def updateStatus(self, current_time):
        # TO DO ajouter des conditions pour blocked, preempted...
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
            print("")
            print("")
            print("")
            print("current_time", current_time)
            print("status", self.status)
            print("remaining_execution_time", self.remaining_execution_time)
            print("activation_time", self.activation_time)
            print("absolute_deadline", self.absolute_deadline)
            print(self.__str__())
            raise Exception("Status Ambigious")