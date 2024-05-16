from modules.scheduling_generation.time_execution import TimeExecution
import time

class EarliestDeadlineFirstVariant1:  
    def updatepriority(self, current_time, taskset, core_number, previous_job):
        priority_list = []
        for task in taskset:
            for job in task:
                if job.status == "Ready":
                    priority_list.append(job)
                    
        priority_list.sort(key=lambda x: x.absolute_deadline, reverse=False)
        if len(priority_list) != 0:
            highest_priority_job = priority_list[0]
        else: 
            highest_priority_job = None

        #priority inversion here if conditions hold
        if previous_job != None and highest_priority_job != None:
            if highest_priority_job != previous_job:
                if previous_job.remaining_execution_time < highest_priority_job.remaining_execution_time and previous_job.remaining_execution_time != 0:
                    highest_priority_job = previous_job
                    

        return highest_priority_job

    def updateStatus(self, current_time, taskset):
        #EDF status can be ready, not ready, finished
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