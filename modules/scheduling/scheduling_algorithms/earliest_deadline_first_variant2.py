import copy

import numpy


class EarliestDeadlineFirstVariant2:
    def __init__(self, taskset, assignment, number_of_cores, scheduling_options, start_time=1, end_time=None):
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.scheduling_options = scheduling_options

        if end_time == None:
            end_time = self.hyperperiod

        self.start_time = start_time
        self.end_time = end_time

        self.assignment = assignment
        self.number_of_cores = number_of_cores
        self.initial_non_preemption_time = self.initiate_non_preemption_time_variant_2()
        self.job_list = [[] for _ in range(self.number_of_cores)]
        self.ready_queue = [[] for _ in range(self.number_of_cores)]
        self.current_jobs = [None] * self.number_of_cores
        self.previous_jobs = [None] * self.number_of_cores
        self.schedule_res = [[] for _ in range(self.number_of_cores)]
        self.non_preemptible_time = {}

        self.total_utilization = 0
        self.actual_utilization = None

    def __str__(self):
        return self.__class__.__name__

    def schedule(self):
        current_time = self.start_time
        self.create_job_list(start_time=self.start_time,
                             end_time=self.end_time)

        while current_time <= self.end_time:
            self.previous_jobs = copy.copy(self.current_jobs)
            for core_index in range(self.number_of_cores):
                self.update_ready_queue(
                    core_index=core_index, current_time=current_time)
                if not self.select_job(core_index=core_index, current_time=current_time):
                    self.total_utilization = None
                    self.actual_utilization = None
                    return self.schedule_res, 0
                self.check_interference(core_index=core_index)

            for core_index in range(self.number_of_cores):
                self.execute_job(core_index=core_index,
                                 current_time=current_time)
            current_time += 1

        # Return schedule and success because no deadline missed at the end of Hyperperiod
        self.actual_utilization = self.total_utilization / self.taskset.hyperperiod
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
        highest_priority_job = None

        for job in self.ready_queue[core_index]:
            if job.relative_deadline >= current_time + 1:
                highest_priority_job = job
                break
            else:
                return False

        previous_job = self.previous_jobs[core_index]

        # Non-preemptible logic
        if previous_job is not None and highest_priority_job is not None:
            if not previous_job.completed and self.non_preemptible_time.get(previous_job, 0) > 0:
                highest_priority_job = previous_job

        self.current_jobs[core_index] = highest_priority_job
        return True

    def execute_job(self, core_index, current_time):
        job_to_execute = self.current_jobs[core_index]
        if job_to_execute:
            self.schedule_res[core_index].append(
                (current_time, job_to_execute.task_number, job_to_execute.job_identifier))
            self.total_utilization += 1
            job_to_execute.execute()
            if job_to_execute.completed:
                self.ready_queue[core_index].remove(job_to_execute)
                self.non_preemptible_time.pop(job_to_execute, None)
            else:
                if job_to_execute != self.previous_jobs[core_index]:
                    self.non_preemptible_time[job_to_execute] = self.initial_non_preemption_time[job_to_execute.task_number]
                else:
                    self.non_preemptible_time[job_to_execute] -= 1
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
                            current_job.apply_interference(
                                interfering_job_id=other_job_id, interfering_interference_factor=other_job.interference_factor)
                            other_job.apply_interference(
                                interfering_job_id=current_job_id, interfering_interference_factor=current_job.interference_factor)

    def initiate_non_preemption_time_variant_2(self):
        non_preemption_criterion = self.scheduling_options["non_preemption_time_variant2"]
        if non_preemption_criterion == "number_of_tasks":
            non_preemption_time = [len(self.taskset)
                                   for _ in range(len(self.taskset))]
        elif non_preemption_criterion == "wcet_of_tasks":
            non_preemption_time = [wcet for wcet in self.taskset.wcet]
        elif non_preemption_criterion == "system_utilization":
            system_utilization = numpy.sum(self.taskset.utilization)
            non_preemption_time = [
                system_utilization for _ in range(len(self.taskset))]
        else:
            print("Invalid criterion, using number of tasks by default")
            non_preemption_time = [len(self.taskset)
                                   for _ in range(len(self.taskset))]
        return non_preemption_time
