from modules.scheduling.scheduling import Scheduling

class CompositeScheduling:
    def __init__(self, scheduler_name):
        self.scheduler_name = scheduler_name
        self.success = True
        self.schedules = []

    def add_schedule(self, schedule):
        if isinstance(schedule, Scheduling):
            self.schedules.append(schedule)
            self.success = self.success & schedule.success
        else:
            raise TypeError("Only Scheduling objects can be added")

    def __str__(self, end_time=None):
        combined_str = f"Combined Scheduler: {self.scheduler_name}\n"
        for schedule in self.schedules:
            schedule_str = schedule.__str__(end_time=end_time)
            if schedule_str != '':
                combined_str += schedule_str + '\n'
        return combined_str

    def __len__(self):
        return len(self.schedules)

    def __getitem__(self, i):
        return self.schedules[i]

