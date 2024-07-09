import time


class EarliestDeadlineFirst:
    def __init__(self, taskset, assignment, number_of_cores, start_time=0, end_time=None):
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        if end_time == None:
            end_time = self.hyperperiod

        self.start_time = start_time
        self.end_time = end_time

        self.assignment = assignment
        self.number_of_cores = number_of_cores
        self.job_list = [[] for _ in range(self.number_of_cores)]
        self.ready_queue = [[] for _ in range(self.number_of_cores)]
        self.current_jobs = [None] * self.number_of_cores
        self.schedule_res = [[] for _ in range(self.number_of_cores)]

    def __str__(self):
        return self.__class__.__name__

    def schedule(self):
        current_time = self.start_time
        self.create_job_list(start_time=self.start_time,
                             end_time=self.end_time)

        while current_time < self.end_time:
            for core_index in range(self.number_of_cores):
                self.update_ready_queue(
                    core_index=core_index, current_time=current_time)
                if not self.select_job(core_index=core_index, current_time=current_time):
                    return self.schedule_res, 0  # Return 0 if deadline missed
                self.check_interference(core_index=core_index)

            for core_index in range(self.number_of_cores):
                self.execute_job(core_index=core_index,
                                 current_time=current_time)
            current_time += 1

        # Return schedule and success because no deadline missed at the end of Hyperperiod
        return self.schedule_res, 1

    def create_job_list(self, start_time, end_time):
        for core_index in range(self.number_of_cores):
            for task_index in (self.assignment[core_index]):
                task = self.taskset[task_index]
                task.create_jobs(start_time=start_time, end_time=end_time)
                self.job_list[core_index].extend(task.job_list)

    def update_ready_queue(self, core_index, current_time):
        for job in self.job_list[core_index]:
            if job.arrival_time == current_time and not job.completed:
                self.ready_queue[core_index].append(job)
        self.ready_queue[core_index].sort(
            key=lambda job: job.relative_deadline)

    def select_job(self, core_index, current_time):
        self.current_jobs[core_index] = None
        for job in self.ready_queue[core_index]:
            if job.relative_deadline >= current_time + 1:
                self.current_jobs[core_index] = job
                break
            else:
                return False
        return True

    def execute_job(self, core_index, current_time):
        job_to_execute = self.current_jobs[core_index]
        if job_to_execute:
            self.schedule_res[core_index].append(
                (current_time, job_to_execute.task_number, job_to_execute.job_identifier))
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
                        # Chaque job garde l'historique des jobs qui ont interferé (pour pas atteindre boucle)
                        other_job_id = f"{other_job.task_number}-{other_job.job_identifier}"
                        current_job_id = f"{current_job.task_number}-{current_job.job_identifier}"
                        if other_job_id not in current_job.interference_history and current_job_id not in other_job.interference_history:
                            current_job.apply_interference(
                                interfering_job_id=other_job_id, interfering_interference_factor=other_job.interference_factor)
                            other_job.apply_interference(
                                interfering_job_id=current_job_id, interfering_interference_factor=current_job.interference_factor)
