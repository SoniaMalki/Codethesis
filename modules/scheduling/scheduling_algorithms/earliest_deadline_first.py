from modules.utils.time_execution import TimeExecution

class EarliestDeadlineFirst:
    def __init__(self, taskset, assignment, number_of_cores):
        self.taskset = taskset
        self.hyperperiod = self.taskset.hyperperiod
        self.assignment = assignment  
        self.number_of_cores = number_of_cores
        self.job_list = [[] for _ in range(self.number_of_cores)] 
        self.ready_queue = [[] for _ in range(self.number_of_cores)] 

    def schedule(self):
        current_time = 0
        schedule = [[] for _ in range(self.number_of_cores)]  

        for core_index in range(self.number_of_cores):
            for task_index in range(len(self.assignment[core_index])):
                task = self.assignment[core_index][task_index]
                task.create_jobs(start_time=current_time, finish_time=self.hyperperiod)
                self.job_list[core_index].extend(task.job_list)

        while current_time < self.hyperperiod:
            for core_index in range(self.number_of_cores):
                for job in self.job_list[core_index]:
                    if job.arrival_time == current_time and not job.completed:
                        self.ready_queue[core_index].append(job)

                self.ready_queue[core_index].sort(key=lambda job: job.relative_deadline)

                job_to_execute = None
                for job in self.ready_queue[core_index]:
                    if job.relative_deadline >= current_time + 1:
                        job_to_execute = job
                        break
                    else:
                        return schedule, 0  
                    
                if job_to_execute:
                    schedule[core_index].append((current_time, job_to_execute.task_number, job_to_execute.job_identifier))
                    job_to_execute.execute(time_slice=1)

                    if job_to_execute.completed:
                        self.ready_queue[core_index].remove(job_to_execute)
                else:
                    schedule[core_index].append((current_time, None, None))

            current_time += 1

        return schedule, 1  