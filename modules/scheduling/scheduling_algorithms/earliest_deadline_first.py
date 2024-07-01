class EarliestDeadlineFirst():
    def __init__(self, taskset, assignment):
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.assignment = assignment
        self.ready_queue = []

    def schedule(self):
        """Schedules the tasks using the Earliest Deadline First (EDF) algorithm."""
        current_time = 0
        schedule = []

        # Initialize the ready queue with jobs from the taskset
        for task in self.taskset:
            task.create_jobs(start_time=current_time, finish_time=self.hyperperiod)
            self.ready_queue.extend(task.job_list)

        while current_time < self.hyperperiod:
            # Sort the ready queue by absolute deadline
            self.ready_queue.sort(key=lambda job: job.relative_deadline)

            # Find the next job to execute
            job_to_execute = None
            for job in self.ready_queue:
                if job.relative_deadline >= current_time + job.wcet:
                    job_to_execute = job
                    break

            # If no job can be scheduled, mark as unsuccessful
            if job_to_execute is None:
                return schedule, False

            # Execute the job for its WCET
            execution_time = min(job_to_execute.wcet, job_to_execute.relative_deadline - current_time)
            schedule.append(
                (current_time, current_time + execution_time, job_to_execute.task_number, job_to_execute.job_identifier)
            )
            current_time += execution_time
            job_to_execute.execute(time_slice=execution_time)

            # Remove completed jobs from the ready queue
            self.ready_queue = [job for job in self.ready_queue if not job.completed]

        return schedule, True