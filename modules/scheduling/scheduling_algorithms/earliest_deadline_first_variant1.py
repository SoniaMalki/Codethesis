import copy
class EarliestDeadlineFirstVariant1:
    def __init__(self, taskset, assignment, number_of_cores):
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.assignment = assignment
        self.number_of_cores = number_of_cores
        self.job_list = [[] for _ in range(self.number_of_cores)]
        self.ready_queue = [[] for _ in range(self.number_of_cores)]
        self.current_jobs = [None] * self.number_of_cores
        self.previous_jobs = [None] * self.number_of_cores
        self.schedule_res = [[] for _ in range(self.number_of_cores)]

    def schedule(self):
        current_time = 0
        self.create_job_list(current_time=current_time)

        while current_time < self.hyperperiod:
            self.previous_jobs = copy.copy(self.current_jobs)
            for core_index in range(self.number_of_cores):
                self.update_ready_queue(core_index=core_index, current_time=current_time)
                if not self.select_job(core_index=core_index, current_time=current_time):
                    return self.schedule_res, 0  # Return 0 if deadline missed
                self.check_interference(core_index=core_index)

            for core_index in range(self.number_of_cores):
                self.execute_job(core_index=core_index, current_time=current_time)
            current_time += 1

        return self.schedule_res, 1  # Return schedule and success because no deadline missed at the end of Hyperperiod

    def create_job_list(self, current_time):
        for core_index in range(self.number_of_cores):
            for task_index in range(len(self.assignment[core_index])):
                task = self.assignment[core_index][task_index]
                task.create_jobs(start_time=current_time, finish_time=self.hyperperiod)
                self.job_list[core_index].extend(task.job_list)

    def update_ready_queue(self, core_index, current_time):
        for job in self.job_list[core_index]:
            if job.arrival_time == current_time and not job.completed:
                self.ready_queue[core_index].append(job)
        self.ready_queue[core_index].sort(key=lambda job: job.relative_deadline)

    def select_job(self, core_index, current_time):
        self.current_jobs[core_index] = None
        highest_priority_job = None

        for job in self.ready_queue[core_index]:
            if job.relative_deadline >= current_time + 1:
                highest_priority_job = job
                break
            else:
                return False
        
        previous_job = self.previous_jobs[core_index]
        # Priority inversion logic
        if previous_job is not None and highest_priority_job is not None:
            if not previous_job.completed:
                if highest_priority_job != previous_job:
                    if previous_job.remaining_execution_time < highest_priority_job.remaining_execution_time and previous_job.remaining_execution_time != 0:
                        highest_priority_job = previous_job
        
        self.current_jobs[core_index] = highest_priority_job
        return True

    def execute_job(self, core_index, current_time):
        job_to_execute = self.current_jobs[core_index]
        if job_to_execute:
            self.schedule_res[core_index].append((current_time, job_to_execute.task_number, job_to_execute.job_identifier))
            job_to_execute.execute()
            if job_to_execute.completed:
                self.ready_queue[core_index].remove(job_to_execute)
        else:
            self.schedule_res[core_index].append((current_time, None, None))

    def check_interference(self, core_index):
        current_job = self.current_jobs[core_index]
        if current_job and current_job.interference_factor > 0 and not current_job.completed:
            for other_core_index in range(self.number_of_cores):
                if other_core_index != core_index:
                    other_job = self.current_jobs[other_core_index]
                    if other_job and other_job.interference_factor > 0 and not other_job.completed:
                        other_job_id = f"{other_job.task_number}-{other_job.job_identifier}"
                        current_job_id = f"{current_job.task_number}-{current_job.job_identifier}"
                        if other_job_id not in current_job.interference_history and current_job_id not in other_job.interference_history:
                            current_job.apply_interference(interfering_job_id=other_job_id, interfering_interference_factor=other_job.interference_factor)
                            other_job.apply_interference(interfering_job_id=current_job_id, interfering_interference_factor=current_job.interference_factor)