from modules.utils.time_execution import TimeExecution

class DeadlineMonotonic: 
    def updatepriority(self, current_time, taskset, core_number, previous_job):
        """Even if we update the priority here for deadline monotonic, it is still static because it is looking at the 
        absolute deadline that is static."""
        priority_list = []
        for task in taskset:
            for job in task:
                if job.status == "Ready":
                    priority_list.append(job)

        priority_list.sort(key=lambda x: x.relative_deadline, reverse=False)
        if len(priority_list) != 0:
            highest_priority_job = priority_list[0]
        else: 
            highest_priority_job = None
            
        return highest_priority_job

    def updateStatus(self, current_time, taskset):
        for task in taskset:
            for job in task.job_list:
                job.updateStatus(current_time)

    def execute(self, current_time, core_number, job_to_execute):
        if job_to_execute != None:
            res = TimeExecution(_time=current_time, _task_index= job_to_execute.task_number, _job_index=job_to_execute.job_identifier)
            job_to_execute.execute(current_time)
        else:
            res = TimeExecution(_time=current_time)
        return res